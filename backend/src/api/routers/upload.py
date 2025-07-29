import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from src.api.services.db_service import DBService, get_db_service
from src.clients.s3_client import get_s3_client
from src.config.settings import settings

router = APIRouter(prefix="/upload", tags=["upload"])


class UploadResponse(BaseModel):
    location: str
    key: str


@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...), db_service: DBService = Depends(get_db_service)
):
    s3_client = get_s3_client()
    key = f"uploads/{uuid.uuid4()}/{file.filename}"
    unique_id = str(uuid.uuid4())

    try:
        file_content = await file.read()

        s3_client.put_object(
            Bucket=settings.S3.bucket_name,
            Key=key,
            Body=file_content,
            ContentType=file.content_type or "application/octet-stream",
        )

        s3_location = f"s3://{settings.S3.bucket_name}/{key}"

        # Create entry using DBService
        db_service.create_entry(unique_id, key, file.filename, s3_location)

        return UploadResponse(location=s3_location, key=key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
