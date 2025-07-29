from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import upload
from .config import get_s3_client, S3_BUCKET_NAME
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
import os

def ensure_s3_bucket():
    """Create S3 bucket if it doesn't exist"""
    client = boto3.client(
        's3',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test'),
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        config=Config(signature_version='s3v4')
    )
    
    try:
        client.head_bucket(Bucket=S3_BUCKET_NAME)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            try:
                client.create_bucket(Bucket=S3_BUCKET_NAME)
                print(f"Created S3 bucket: {S3_BUCKET_NAME}")
            except ClientError as create_error:
                print(f"Failed to create bucket: {create_error}")
                raise

app = FastAPI(
    title="Document Processing API",
    description="API for document processing with OCR and AI capabilities",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    ensure_s3_bucket()

@app.get("/")
async def root():
    return {"message": "Document Processing API", "status": "operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}