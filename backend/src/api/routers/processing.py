from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.services.db_service import DBService, get_db_service
from src.worker.tasks import process_document_task

router = APIRouter(prefix="/processing", tags=["processing"])


class ProcessingRequest(BaseModel):
    entry_id: str
    s3_location: str


class ProcessingResponse(BaseModel):
    task_id: str
    entry_id: str
    status: str


class JobStatus(BaseModel):
    id: str
    key: str
    filename: str
    location: str
    status: str
    progress: int
    processing_job: Optional[str] = None
    created_at: str
    updated_at: str


class DocumentSummaryResponse(BaseModel):
    document_summary: str
    primary_topics: List[str]


@router.post("/submit-job", response_model=ProcessingResponse)
async def submit_job(request: ProcessingRequest):
    """Start document processing by sending task to Redis queue"""
    try:
        # Send task to Redis queue
        task = process_document_task.delay(request.entry_id, request.s3_location)

        return ProcessingResponse(
            task_id=task.id, entry_id=request.entry_id, status="queued"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start processing: {str(e)}"
        )


@router.get("/status/{entry_id}", response_model=JobStatus)
async def get_job_status(
    entry_id: str, db_service: DBService = Depends(get_db_service)
):
    """Get the status of a processing job from the database"""
    try:
        # Get all entries and find the one with matching ID
        entries = db_service.get_all()
        job = next((entry for entry in entries if entry["id"] == entry_id), None)

        if not job:
            raise HTTPException(status_code=404, detail=f"Job {entry_id} not found")

        return JobStatus(**job)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Job {entry_id} not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/summary/{entry_id}", response_model=DocumentSummaryResponse)
async def get_document_summary(
    entry_id: str, db_service: DBService = Depends(get_db_service)
):
    """Get the final summary of a processed document"""
    try:
        # Get the entry from the database
        entry = db_service.get_entry(entry_id)

        # Check if the document has been processed
        if entry.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Document {entry_id} is not yet fully processed. Current status: {entry.get('status')}",
            )

        # Check if final_summary exists
        final_summary = entry.get("final_summary")
        if not final_summary:
            raise HTTPException(
                status_code=404, detail=f"No summary found for document {entry_id}"
            )

        # Extract document_summary and primary_topics
        document_summary = final_summary.get("document_summary", "")
        primary_topics = final_summary.get("primary_topics", [])

        if not document_summary:
            raise HTTPException(
                status_code=404, detail=f"Document summary not found for {entry_id}"
            )

        return DocumentSummaryResponse(
            document_summary=document_summary, primary_topics=primary_topics
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Document {entry_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get document summary: {str(e)}"
        )
