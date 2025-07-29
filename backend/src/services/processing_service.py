import asyncio
import io
import json
import os
from datetime import datetime, timezone

import numpy as np

from src.services.db_service import DBService
from src.services.gen_ai.summary_service import SummaryService
from src.services.loaders.pdf_loader import PdfChunkDocumentLoader
from src.services.s3_service import get_s3_service


class PDFProcessingService:
    def __init__(self, db_service: DBService):
        self.db_service = db_service
        self.s3_service = get_s3_service()
        self.summary_service = SummaryService()
        self.chunk_progress = {}

    def process_document(self, entry_id: str, s3_location: str):
        """Process PDF document by extracting chunks and storing in database"""
        # Update status to processing
        self.db_service.update_progress(entry_id, 0, "processing")

        try:
            # Extract S3 key from s3_location (format: s3://bucket/key)
            s3_key = s3_location.replace("s3://", "").split("/", 1)[1]

            # Read file bytes from S3
            file_bytes = self.s3_service.read_file(s3_key)

            # Initialize PDF chunk loader
            pdf_loader = PdfChunkDocumentLoader(chunk_size=25000, overlap=500)

            # Extract chunks from PDF
            chunks = pdf_loader.extract_chunks(io_stream=file_bytes)

            # Initialize progress tracking
            self.chunk_progress = {i: 0 for i in range(len(chunks))}

            # ---- Run chunk processing asynchronously ----
            processed_chunks = asyncio.run(self._process_all_chunks(entry_id, chunks))

            # Get final document summary from all processed chunks
            final_summary = self.summary_service.get_final_summary(processed_chunks)
            print(f"Generated final summary: {final_summary}")

            # Store processed chunks in the database
            self._store_chunks(entry_id, processed_chunks, final_summary)
            print(f"Extracted and processed {len(chunks)} chunks from PDF")

            # Update final status
            self.db_service.update_progress(entry_id, 100, "completed")

            return {
                "entry_id": entry_id,
                "s3_location": s3_location,
                "status": "completed",
                "chunks_count": len(processed_chunks),
            }

        except Exception as e:
            print(f"Error processing document: {e}")
            self.db_service.update_progress(entry_id, 0, "failed")
            return {
                "entry_id": entry_id,
                "s3_location": s3_location,
                "status": "failed",
                "error": str(e),
            }

    async def _process_all_chunks(self, entry_id: str, chunks: list):
        """Process all PDF chunks concurrently (max 5 at a time)."""
        semaphore = asyncio.Semaphore(10)

        async def process_with_progress_update(chunk, index):
            async with semaphore:
                # Run the blocking summary call in a thread
                summary_result = await asyncio.to_thread(
                    self.summary_service.get_chunk_summary,
                    chunk.start_page,
                    chunk.end_page,
                    chunk.content,
                )

                # Add summary to chunk
                chunk_dict = chunk.model_dump()
                chunk_dict["summary"] = summary_result

                # Mark chunk as processed
                self.chunk_progress[index] = 1

                # Update overall progress
                progress_mean = self.get_chunk_progress()
                overall_progress = min(round(progress_mean * 100, 1), 99)
                self.db_service.update_progress(
                    entry_id, int(overall_progress), "processing"
                )

                print(f"Completed chunk {index}, progress: {overall_progress}%")
                return chunk_dict

        # Launch tasks for all chunks
        tasks = [
            asyncio.create_task(process_with_progress_update(chunk, i))
            for i, chunk in enumerate(chunks)
        ]
        return await asyncio.gather(*tasks)

    def get_chunk_progress(self) -> float:
        """Get the mean progress of all chunks using numpy"""
        if not self.chunk_progress:
            return 0.0
        return np.mean(list(self.chunk_progress.values()))

    def _store_chunks(
        self, entry_id: str, chunks_json: list, final_summary: dict = None
    ):
        """Store PDF chunks and final summary in the database by updating the entry"""
        json_file_path = os.path.join(self.db_service.base_dir, f"{entry_id}.json")

        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"Entry {entry_id} not found")

        # Read existing entry
        with open(json_file_path, "r") as f:
            entry_data = json.load(f)

        # Add chunks, final summary & update timestamp
        entry_data["chunks"] = chunks_json
        if final_summary:
            entry_data["final_summary"] = final_summary
            # Extract and store primary topics as key terms for easier access
            if "primary_topics" in final_summary:
                entry_data["key_terms"] = final_summary["primary_topics"]
        entry_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Write back to file
        with open(json_file_path, "w") as f:
            json.dump(entry_data, f, indent=2)
