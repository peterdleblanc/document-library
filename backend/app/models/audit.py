"""Audit log model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # upload, download, delete, update, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # document, user, tag, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(JSON, nullable=True)  # Flexible field for action-specific data
    result = Column(String(20), default="success", nullable=False)  # success, failure, unauthorized
    error_message = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type}>"
