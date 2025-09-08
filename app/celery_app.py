from celery import Celery
from app.config import settings

# Initialize Celery application for background task processing
celery_app = Celery(
    "backend_app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

# Configure Celery task serialization and timezone settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_serializer_kwargs={
        'ensure_ascii': False
    },
)
