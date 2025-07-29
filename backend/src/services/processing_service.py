import io
import json
import random
import time

from src.services.db_service import DBService
from src.services.loaders.pdf_loader import PdfChunkDocumentLoader
from src.services.s3_service import get_s3_service


class PDFProcessingService:
    def __init__(self, db_service: DBService):
        self.db_service = db_service
        self.s3_service = get_s3_service()

    def process_document(self, entry_id: str, s3_location: str):
        """Process PDF document by extracting chunks and storing in database"""
        # Update status to processing
        self.db_service.update_progress(entry_id, 0, "processing")

        try:
            # Extract S3 key from s3_location (format: s3://bucket/key)
            s3_key = s3_location.replace("s3://", "").split("/", 1)[1]

            # Read file bytes from S3
            file_bytes = self.s3_service.read_file(s3_key)
            self.db_service.update_progress(entry_id, 20, "processing")

            # Initialize PDF chunk loader with specified parameters
            pdf_loader = PdfChunkDocumentLoader(chunk_size=25000, overlap=500)
            self.db_service.update_progress(entry_id, 40, "processing")

            # Extract chunks from PDF
            chunks = pdf_loader.extract_chunks(io_stream=file_bytes)
            self.db_service.update_progress(entry_id, 80, "processing")

            # Convert chunks to JSON using model.dump() and store in database
            chunks_json = [chunk.model_dump() for chunk in chunks]

            print(chunks_json)

            # Store chunks in database by updating the entry
            self._store_chunks(entry_id, chunks_json)
            print(f"Extracted {len(chunks)} chunks from PDF")

            self.db_service.update_progress(entry_id, 100, "completed")

            return {
                "entry_id": entry_id,
                "s3_location": s3_location,
                "status": "completed",
                "chunks_count": len(chunks),
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

    def _store_chunks(self, entry_id: str, chunks_json: list):
        """Store PDF chunks in the database by updating the entry"""
        import os

        json_file_path = os.path.join(self.db_service.base_dir, f"{entry_id}.json")

        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"Entry {entry_id} not found")

        # Read existing data
        with open(json_file_path, "r") as f:
            entry_data = json.load(f)

        # Add chunks data
        entry_data["chunks"] = chunks_json
        from datetime import datetime, timezone

        entry_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Write back to file
        with open(json_file_path, "w") as f:
            json.dump(entry_data, f, indent=2)
