import boto3
from botocore.client import Config

from src.config.settings import settings


def get_s3_client():
    client = boto3.client(
        "s3",
        endpoint_url=settings.S3.endpoint_url,
        aws_access_key_id=settings.S3.access_key_id,
        aws_secret_access_key=settings.S3.secret_access_key,
        region_name=settings.S3.region_name,
        config=Config(signature_version="s3v4"),
    )

    return client
