"""Services package"""
from app.services.minio_service import minio_service
from app.services.document_service import document_service

__all__ = ["minio_service", "document_service"]
