"""Celery application configuration"""
from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "document_library",
    broker=settings.CELERY_BROKER_URL or settings.REDIS_URL,
    backend=settings.CELERY_RESULT_BACKEND or settings.REDIS_URL,
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time for better control
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
)

# Auto-discover tasks from tasks module
celery_app.autodiscover_tasks(["app.tasks"])

# Optional: Configure beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Example: cleanup old temporary files
    # 'cleanup-temp-files': {
    #     'task': 'app.tasks.document_tasks.cleanup_temp_files',
    #     'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    # },
}
