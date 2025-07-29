from io import BytesIO
from typing import Optional

from src.clients.s3_client import get_s3_client
from src.config.settings import settings


class S3Service:
    def __init__(self):
        self.s3_client = get_s3_client()

    def upload_file(
        self, key: str, file_content: bytes, content_type: Optional[str] = None
    ) -> str:
        self.s3_client.put_object(
            Bucket=settings.S3.bucket_name,
            Key=key,
            Body=file_content,
            ContentType=content_type or "application/octet-stream",
        )
        return f"s3://{settings.S3.bucket_name}/{key}"

    def read_file(self, key: str) -> BytesIO:
        response = self.s3_client.get_object(Bucket=settings.S3.bucket_name, Key=key)
        return BytesIO(response["Body"].read())


def get_s3_service() -> S3Service:
    return S3Service()
