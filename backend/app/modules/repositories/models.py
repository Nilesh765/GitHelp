import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.common.base import Base
from app.common.enums import RepoProvider, RepoStatus

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    url = Column(String(2048), nullable=False)
    name = Column(String(255), nullable=True)
    provider = Column(Enum(RepoProvider), nullable=False)
    is_private = Column(Boolean, default=False, nullable=False)
    default_branch = Column(String(100), default="main", nullable=False)
    
    celery_task_id = Column(String(255), nullable=True, index=True)
    status = Column(Enum(RepoStatus), default=RepoStatus.pending, nullable=False, index=True)
    error_message = Column(Text, nullable=True)

    metadata_ = Column("metadata", JSONB, nullable=True)
    analysis_config = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="repositories")
    reviews = relationship("Review", back_populates="repository", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Repository id={self.id}, name={self.name}, status={self.status}>"