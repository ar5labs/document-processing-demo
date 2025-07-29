from typing import Optional

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
