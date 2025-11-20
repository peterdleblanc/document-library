"""Document models"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    original_filename = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # bytes
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256
    storage_path = Column(String(1000), nullable=False)  # Path in MinIO

    # Metadata
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    current_version_id = Column(UUID(as_uuid=True), ForeignKey("document_versions.id"), nullable=True)

    # Processing status
    processing_status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    processing_progress = Column(Integer, default=0, nullable=False)  # 0-100

    # Relationships
    uploader = relationship("User", back_populates="documents", foreign_keys=[uploaded_by])
    versions = relationship("DocumentVersion", back_populates="document", foreign_keys="DocumentVersion.document_id")
    current_version = relationship("DocumentVersion", foreign_keys=[current_version_id], post_update=True)
    metadata = relationship("DocumentMetadata", back_populates="document", uselist=False)
    text_content = relationship("DocumentText", back_populates="document", uselist=False)
    embeddings = relationship("DocumentEmbedding", back_populates="document")

    def __repr__(self):
        return f"<Document {self.title}>"


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    storage_path = Column(String(1000), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_hash = Column(String(64), nullable=False)
    change_summary = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    document = relationship("Document", back_populates="versions", foreign_keys=[document_id])
    creator = relationship("User")

    def __repr__(self):
        return f"<DocumentVersion {self.document_id} v{self.version_number}>"


class DocumentText(Base):
    __tablename__ = "document_text"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("document_versions.id"), nullable=False)
    extracted_text = Column(Text, nullable=True)
    ocr_applied = Column(Boolean, default=False, nullable=False)
    extraction_method = Column(String(100), nullable=True)  # tika, pymupdf, tesseract, textract
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="text_content")
    version = relationship("DocumentVersion")

    def __repr__(self):
        return f"<DocumentText {self.document_id}>"


class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("document_versions.id"), nullable=False)

    # Built-in metadata
    author = Column(String(255), nullable=True)
    created_date = Column(DateTime, nullable=True)
    modified_date = Column(DateTime, nullable=True)
    language = Column(String(10), nullable=True)
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)

    # AI-generated metadata
    auto_tags = Column(ARRAY(String), default=list, nullable=False)
    categories = Column(ARRAY(String), default=list, nullable=False)
    summary = Column(Text, nullable=True)
    entities = Column(JSON, nullable=True)  # people, orgs, dates, amounts

    # Full metadata as JSON
    metadata_json = Column(JSON, nullable=True)

    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ai_model_used = Column(String(100), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="metadata")
    version = relationship("DocumentVersion")

    def __repr__(self):
        return f"<DocumentMetadata {self.document_id}>"


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("document_versions.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    # Note: embedding_vector will be added as a vector type after pgvector extension is enabled
    # embedding_vector = Column(Vector(1536), nullable=False)
    model_used = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="embeddings")
    version = relationship("DocumentVersion")

    def __repr__(self):
        return f"<DocumentEmbedding {self.document_id} chunk {self.chunk_index}>"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    color = Column(String(7), nullable=True)  # Hex color
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Tag {self.name}>"
