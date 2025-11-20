"""Document endpoints"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.api.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all documents for current user"""
    # Calculate offset
    offset = (page - 1) * page_size

    # Get total count
    count_result = await db.execute(
        select(Document).where(Document.uploaded_by == current_user.id)
    )
    total = len(count_result.all())

    # Get paginated documents
    result = await db.execute(
        select(Document)
        .where(Document.uploaded_by == current_user.id)
        .order_by(Document.uploaded_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    documents = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "documents": documents
    }


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific document"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.uploaded_by == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a new document"""
    # This is a stub - will be implemented in Phase 1
    # Will handle file upload to MinIO and create database record
    return {
        "message": "Upload endpoint - to be implemented",
        "filename": file.filename,
        "title": title or file.filename
    }


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.uploaded_by == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    await db.delete(document)
    await db.commit()

    return None
