import uuid
from sqlalchemy import Column, String, ForeignKey, Enum, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import relationship
from app.common.base import Base
from app.common.enums import ReviewStatus, AnalysisMode

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    repository_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    commit_sha = Column(String(40), nullable=True)
    analysis_mode = Column(Enum(AnalysisMode), nullable=False, default=AnalysisMode.full)
    status = Column(Enum(ReviewStatus), nullable=False, default=ReviewStatus.pending)

    quality_score = Column(Integer, nullable=True)
    security_score = Column(Integer, nullable=True)
    maintainability_score = Column(Integer, nullable=True)
    performance_score = Column(Integer, nullable=True)
    
    critical_count = Column(Integer, default=0)
    major_count = Column(Integer, default=0)
    minor_count = Column(Integer, default=0)
    info_count = Column(Integer, default=0)

    summary = Column(Text, nullable=True)
    top_issues = Column(JSONB, nullable=True)
    
    total_tokens_used = Column(Integer, default=0)
    llm_calls_made = Column(Integer, default=0)
    analysis_duration_ms = Column(Integer, nullable=True)
    
    repository = relationship("Repository", back_populates="reviews")