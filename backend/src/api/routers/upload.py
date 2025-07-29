from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import uuid
import json
import os
from datetime import datetime
from ..config import get_s3_client, S3_BUCKET_NAME
router = APIRouter(prefix="/upload", tags=["upload"])

class UploadResponse(BaseModel):
    location: str
    key: str

@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    s3_client = get_s3_client()
    key = f"uploads/{uuid.uuid4()}/{file.filename}"
    unique_id = str(uuid.uuid4())

    try:
        file_content = await file.read()
        
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=key,
            Body=file_content,
            ContentType=file.content_type or "application/octet-stream"
        )
        
        s3_location = f"s3://{S3_BUCKET_NAME}/{key}"
        
        # Create JSON file in uploads folder to mimic NoSQL database
        upload_record = {
            "id": unique_id,
            "key": key,
            "filename": file.filename,
            "location": s3_location,
            "status": "queued",
            "progress": 0,
            "processing_job": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Ensure uploads directory exists
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Write JSON file
        json_file_path = os.path.join(uploads_dir, f"{unique_id}.json")
        with open(json_file_path, 'w') as f:
            json.dump(upload_record, f, indent=2)
        
        return UploadResponse(
            location=s3_location,
            key=key
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")