import os

from pydantic import BaseModel


class S3Settings(BaseModel):
    bucket_name: str
    region_name: str
    access_key_id: str
    secret_access_key: str
    endpoint_url: str


class RedisSettings(BaseModel):
    url: str
    host: str
    port: int
    db: int


class AppSettings(BaseModel):
    S3: S3Settings
    Redis: RedisSettings


settings = AppSettings(
    S3=S3Settings(
        bucket_name=os.getenv("S3_BUCKET_NAME", "document-processing-bucket"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
    ),
    Redis=RedisSettings(
        url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
    ),
)
