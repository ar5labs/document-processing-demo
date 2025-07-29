import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from src.api.services.db_service import DBService, get_db_service
from src.api.services.s3_service import S3Service, get_s3_service

router = APIRouter(prefix="/upload", tags=["upload"])


class UploadResponse(BaseModel):
    location: str
    key: str


@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db_service: DBService = Depends(get_db_service),
    s3_service: S3Service = Depends(get_s3_service),
):
    key = f"uploads/{uuid.uuid4()}/{file.filename}"
    unique_id = str(uuid.uuid4())

    try:
        file_content = await file.read()

        s3_location = s3_service.upload_file(key, file_content, file.content_type)

        # Create entry using DBService

        print(f"creating db entry {s3_location}")
        db_service.create_entry(unique_id, key, file.filename, s3_location)

        return UploadResponse(location=s3_location, key=key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
