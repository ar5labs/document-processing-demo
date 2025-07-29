import os
from dataclasses import dataclass

@dataclass
class S3Config:
    bucket_name: str
    region_name: str
    access_key_id: str
    secret_access_key: str
    endpoint_url: str

def get_s3_config() -> S3Config:
    return S3Config(
        bucket_name=os.getenv('S3_BUCKET_NAME', 'document-processing-bucket'),
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test'),
        endpoint_url=os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566')
    )