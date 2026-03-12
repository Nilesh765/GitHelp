import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.common.base import Base
from app.common.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)

    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    github_user_id = Column(String(100), unique=True, nullable=True)
    github_token_enc = Column(String(512), nullable=True)
    gitlab_user_id = Column(String(100), unique=True, nullable=True)
    gitlab_token_enc = Column(String(512), nullable=True)

    refresh_token_hash = Column(String(255), nullable=True)
    refresh_token_exp = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # repositories = relationship("Repository", back_populates="owner", cascade="all, delete-orphan")
    # api_keys = relationship("Apikey", back_populates="user", cascade="all, delete-orphan")
