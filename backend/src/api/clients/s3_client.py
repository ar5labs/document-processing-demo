from src.config.settings import S3Config, get_s3_config
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError


def get_s3_client(config: S3Config = None):
    if config is None:
        config = get_s3_config()
    
    client = boto3.client(
        's3',
        endpoint_url=config.endpoint_url,
        aws_access_key_id=config.access_key_id,
        aws_secret_access_key=config.secret_access_key,
        region_name=config.region_name,
        config=Config(signature_version='s3v4')
    )
    
    return client