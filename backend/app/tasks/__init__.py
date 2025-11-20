"""Tasks package for Celery background jobs"""
from app.tasks.document_tasks import process_document

__all__ = ["process_document"]
