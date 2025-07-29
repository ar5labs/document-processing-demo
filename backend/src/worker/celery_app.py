from celery import Celery
import os

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery(
    "document_processing",
    broker=redis_url,
    backend=redis_url,
    include=["src.worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)