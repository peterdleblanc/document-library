"""Document service for business logic"""
import os
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import UploadFile
from app.models.document import Document, DocumentVersion
from app.services.minio_service import minio_service, calculate_file_hash
from app.schemas.document import DocumentResponse, DocumentListResponse


class DocumentService:
    """Service for document operations"""

    @staticmethod
    async def create_document(
        db: AsyncSession,
        file: UploadFile,
        user_id: UUID,
        title: Optional[str] = None
    ) -> Document:
        """
        Create a new document with file upload

        Args:
            db: Database session
            file: Uploaded file
            user_id: ID of user uploading the document
            title: Optional custom title (defaults to filename)

        Returns:
            Document: Created document record
        """
        # Use filename as title if not provided
        if not title:
            title = file.filename or "Untitled Document"

        # Read file content
        file_content = await file.read()
        file.file.seek(0)  # Reset for hash calculation

        # Calculate file hash and size
        file_hash, file_size = calculate_file_hash(file.file)

        # Check for duplicate files
        existing = await db.execute(
            select(Document).where(Document.file_hash == file_hash)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Document with same content already exists")

        # Generate storage path: documents/{year}/{month}/{document_id}/original.ext
        now = datetime.utcnow()
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ""

        # Create document record first to get ID
        document = Document(
            title=title,
            original_filename=file.filename or "unknown",
            mime_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            file_hash=file_hash,
            uploaded_by=user_id,
            storage_path="",  # Will update after upload
            processing_status="pending",
            processing_progress=0
        )

        db.add(document)
        await db.flush()  # Get document ID without committing

        # Generate storage path with document ID
        storage_path = f"documents/{now.year}/{now.month:02d}/{document.id}/v1{file_ext}"
        document.storage_path = storage_path

        # Upload to MinIO
        file.file.seek(0)  # Reset file pointer
        minio_service.upload_file(
            file_data=file.file,
            object_name=storage_path,
            content_type=file.content_type or "application/octet-stream",
            file_size=file_size
        )

        # Create initial version record
        version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            storage_path=storage_path,
            file_size=file_size,
            file_hash=file_hash,
            change_summary="Initial upload",
            created_by=user_id
        )

        db.add(version)
        await db.flush()

        # Set current version
        document.current_version_id = version.id

        await db.commit()
        await db.refresh(document)

        # Trigger background processing task
        from app.tasks.document_tasks import process_document
        process_document.delay(str(document.id))

        return document

    @staticmethod
    async def get_document(db: AsyncSession, document_id: UUID, user_id: UUID) -> Optional[Document]:
        """
        Get a document by ID (with user authorization check)

        Args:
            db: Database session
            document_id: Document ID
            user_id: User ID requesting the document

        Returns:
            Document or None
        """
        result = await db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.uploaded_by == user_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_documents(
        db: AsyncSession,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None
    ) -> DocumentListResponse:
        """
        List documents for a user with pagination

        Args:
            db: Database session
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Number of items per page
            search: Optional search query

        Returns:
            DocumentListResponse with paginated documents
        """
        offset = (page - 1) * page_size

        # Build query
        query = select(Document).where(Document.uploaded_by == user_id)

        # Add search filter if provided
        if search:
            query = query.where(
                Document.title.ilike(f"%{search}%") |
                Document.original_filename.ilike(f"%{search}%")
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.order_by(Document.uploaded_at.desc()).offset(offset).limit(page_size)
        result = await db.execute(query)
        documents = result.scalars().all()

        return DocumentListResponse(
            total=total,
            page=page,
            page_size=page_size,
            documents=documents
        )

    @staticmethod
    async def delete_document(db: AsyncSession, document_id: UUID, user_id: UUID) -> bool:
        """
        Delete a document and its file from storage

        Args:
            db: Database session
            document_id: Document ID
            user_id: User ID (for authorization)

        Returns:
            bool: True if deleted successfully
        """
        # Get document
        document = await DocumentService.get_document(db, document_id, user_id)
        if not document:
            return False

        # Delete file from MinIO
        try:
            minio_service.delete_file(document.storage_path)
        except Exception as e:
            print(f"Error deleting file from MinIO: {e}")
            # Continue with database deletion even if MinIO fails

        # Delete from database (cascade will handle versions, metadata, etc.)
        await db.delete(document)
        await db.commit()

        return True

    @staticmethod
    async def get_download_url(db: AsyncSession, document_id: UUID, user_id: UUID) -> Optional[str]:
        """
        Generate a presigned download URL for a document

        Args:
            db: Database session
            document_id: Document ID
            user_id: User ID (for authorization)

        Returns:
            str: Presigned URL or None if document not found
        """
        document = await DocumentService.get_document(db, document_id, user_id)
        if not document:
            return None

        return minio_service.get_file_url(document.storage_path)


# Singleton instance
document_service = DocumentService()
