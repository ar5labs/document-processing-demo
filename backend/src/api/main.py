from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import upload
from src.clients.s3_client import get_s3_client
from src.config.settings import settings


def ensure_s3_bucket():
    """Create S3 bucket if it doesn't exist"""
    client = get_s3_client()

    try:
        client.head_bucket(Bucket=settings.S3.bucket_name)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            try:
                client.create_bucket(Bucket=settings.S3.bucket_name)
                print(f"Created S3 bucket: {settings.S3.bucket_name}")
            except ClientError as create_error:
                print(f"Failed to create bucket: {create_error}")
                raise


app = FastAPI(
    title="Document Processing API",
    description="API for document processing with OCR and AI capabilities",
    version="1.0.0",
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
