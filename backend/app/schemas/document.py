"""Document schemas for request/response validation"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document schema"""
    title: str = Field(..., min_length=1, max_length=500)


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)


class DocumentMetadataSchema(BaseModel):
    """Schema for document metadata"""
    author: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    language: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    auto_tags: List[str] = []
    categories: List[str] = []
    summary: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class DocumentVersionSchema(BaseModel):
    """Schema for document version"""
    id: UUID
    version_number: int
    file_size: int
    file_hash: str
    change_summary: Optional[str] = None
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: UUID
    original_filename: str
    mime_type: str
    file_size: int
    file_hash: str
    uploaded_by: UUID
    uploaded_at: datetime
    processing_status: str
    processing_progress: int
    metadata: Optional[DocumentMetadataSchema] = None
    current_version_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    """Schema for detailed document response with versions"""
    versions: List[DocumentVersionSchema] = []


class DocumentListResponse(BaseModel):
    """Schema for paginated document list"""
    total: int
    page: int
    page_size: int
    documents: List[DocumentResponse]


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    document_id: UUID
    status: str
    message: str


class DocumentSearchRequest(BaseModel):
    """Schema for document search request"""
    query: str = Field(..., min_length=1)
    filters: Optional[Dict[str, Any]] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class DocumentSearchResult(BaseModel):
    """Schema for a single search result"""
    id: UUID
    title: str
    snippet: Optional[str] = None
    score: float
    metadata: Optional[Dict[str, Any]] = None


class DocumentSearchResponse(BaseModel):
    """Schema for search results"""
    total: int
    page: int
    page_size: int
    query: str
    results: List[DocumentSearchResult]
    facets: Optional[Dict[str, Any]] = None
