import io
from pathlib import Path
from typing import List, Union

import pymupdf
from langchain.text_splitter import CharacterTextSplitter
from pydantic import BaseModel


class PDFPage(BaseModel):
    page_number: int
    content: str
    total_pages: int


class PDFChunk(BaseModel):
    content: str
    start_page: int
    end_page: int
    total_pages: int


class PdfDocumentLoader:
    def __init__(self):
        pass

    @staticmethod
    def get_document_length(pdf_path: Path | str = None, io_stream: io.BytesIO = None):
        """returns the number of document models to process"""
        if pdf_path:
            pdf_file = pymupdf.open(pdf_path)
        elif io_stream:
            pdf_file = pymupdf.open(stream=io_stream.read(), filetype="pdf")
        else:
            raise ValueError("Either 'pdf_path' or 'io_stream' must be provided.")

        return pdf_file.page_count

    @staticmethod
    def extract_pages(
        pdf_path: Path | str = None, io_stream: io.BytesIO = None
    ) -> List[PDFPage]:
        """Extract all PDF pages' content."""

        if pdf_path:
            pdf_file = pymupdf.open(pdf_path)
        elif io_stream:
            io_stream.seek(0)
            pdf_file = pymupdf.open(stream=io_stream.read(), filetype="pdf")
        else:
            raise ValueError("Either 'pdf_path' or 'io_stream' must be provided.")

        pages = []
        for page_number in range(pdf_file.page_count):
            page = pdf_file[page_number]
            text = page.get_text().strip()

            pages.append(
                PDFPage(
                    page_number=page_number + 1,
                    content=text,
                    total_pages=pdf_file.page_count,
                )
            )

        pdf_file.close()
        return pages


class PdfChunkDocumentLoader:
    def __init__(self, chunk_size: int = 0, overlap: int = 0):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")
        if overlap < 0:
            raise ValueError("overlap must be a non-negative integer")
        if overlap >= chunk_size:
            raise ValueError("overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.pages = []

    @staticmethod
    def get_document_length(pdf_path: Path | str = None, io_stream: io.BytesIO = None):
        """returns the number of document models to process"""
        if pdf_path:
            pdf_file = pymupdf.open(pdf_path)
        elif io_stream:
            pdf_file = pymupdf.open(stream=io_stream.read(), filetype="pdf")
        else:
            raise ValueError("Either 'pdf_path' or 'io_stream' must be provided.")

        return pdf_file.page_count

    def extract_chunks(
        self, pdf_path: Union[Path, str] = None, io_stream: io.BytesIO = None
    ) -> List[PDFChunk]:
        # Load all pages using PdfDocumentLoader
        if not self.pages:
            self.pages = PdfDocumentLoader.extract_pages(pdf_path, io_stream)

        if not self.pages:
            return []

        # Prepare combined text and track page ranges
        combined_text = ""
        page_ranges = []
        for page in self.pages:
            # Include page number before the content
            page_content = f"[Page {page.page_number}]\n{page.content}\n"
            start = len(combined_text)
            combined_text += page_content
            end = start + len(page_content) - 1  # end is inclusive
            page_ranges.append((start, end, page.page_number))

        # Initialize the text splitter
        splitter = CharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap,
            separator="\n",
            length_function=len,
        )
        chunks = splitter.split_text(combined_text)

        pdf_chunks = []
        # Track current position to estimate chunk indices
        current_position = 0
        for chunk in chunks:
            chunk_length = len(chunk)
            start_idx = current_position
            end_idx = start_idx + chunk_length

            # Find contributing pages based on estimated indices
            contributing_pages = set()
            for p_start, p_end, p_num in page_ranges:
                if not (p_end < start_idx or p_start > end_idx):
                    contributing_pages.add(p_num)

            if not contributing_pages:
                continue

            contributing_pages = sorted(contributing_pages)

            # Add the PDFChunk
            pdf_chunks.append(
                PDFChunk(
                    content=chunk.strip(),
                    start_page=contributing_pages[0],
                    end_page=contributing_pages[-1],
                    total_pages=self.pages[0].total_pages,
                )
            )

            # Update current position for next chunk, considering overlap
            current_position = end_idx - self.overlap

        return pdf_chunks
