import time

from celery import Task

from src.services.db_service import get_db_service
from src.services.processing_service import PDFProcessingService

from .celery_app import celery_app


class CallbackTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        # Update job status to completed
        from ..api.models import JobStatus, update_job

        job_id = args[0] if args else None
        if job_id:
            update_job(
                job_id,
                status=JobStatus.COMPLETED,
                processing_progress=100,
                status_message="Document successfully processed and ready for viewing",
            )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # Update job status to failed
        from ..api.models import JobStatus, update_job

        job_id = args[0] if args else None
        if job_id:
            update_job(
                job_id,
                status=JobStatus.FAILED,
                error_message=str(exc),
                status_message=f"Processing failed: {str(exc)}",
            )


@celery_app.task(bind=True, base=CallbackTask, name="process_document")
def process_document(self, job_id: str, file_path: str):
    from ..api.models import JobStatus, update_job

    # Update progress to 25%
    update_job(
        job_id, processing_progress=25, status_message="Extracting text from document"
    )
    time.sleep(2)

    # Update progress to 50%
    update_job(
        job_id, processing_progress=50, status_message="Analyzing document structure"
    )
    time.sleep(2)

    # Update progress to 75%
    update_job(
        job_id, processing_progress=75, status_message="Generating document summary"
    )
    time.sleep(2)

    # Final update happens in on_success callback
    return {
        "job_id": job_id,
        "status": "completed",
        "result": "Document processed successfully",
    }


@celery_app.task(name="extract_text")
def extract_text(file_path: str):
    return {"file_path": file_path, "text": "Extracted text placeholder", "pages": 1}


@celery_app.task(name="process_document_task")
def process_document_task(entry_id: str, s3_location: str):
    """Celery task that processes a document using the PDFProcessingService"""
    db_service = get_db_service()
    processing_service = PDFProcessingService(db_service)

    return processing_service.process_document(entry_id, s3_location)
