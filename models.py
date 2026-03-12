from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime, Text, Float, UniqueConstraint
from sqlalchemy.dialect.postgresql import UUID,JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pg.vector.sqlalchemy import vector
import enum, uuid

from app.core.database import Base

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    manager = "manager"

class RepoStatus(str, enum.Enum):
    pending = "pending"
    cloning = "cloning"
    analyzing = "analyzing"
    completed = "completed"
    failed = "failed"

class RepoProvider(str, enum.Enum):
    github = "github"
    gitlab = "gitlab"
    other = "other"

class ReviewStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"

class FindingSeverity(str, enum.Enum):
    critical = "critical"
    major = "major"
    minor = "minor"
    style = "style"

class FindingCategory(str, enum.Enum):
    security = "security"
    performance = "performance"
    maintainability = "maintainability"
    architecture = "architecture"
    style = "style"
    documentation = "documentation"
    

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    emai = Column(String, unique=True, index=True)
    role = Column(String, unique=True, index=True)
    repos = relationship("Repository", back_populates="owner")

class Repository(Base):
    __tablename__ = "repositories"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="repos")
    chunks = relationship("CodeChunk", back_populates="repo")
    reviews = relationship("Review", back_populates="repo")

class CodeChunk(Base):
    __tablename__ = "code_chunks"
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    repo = relationship("Repository", back_populates="chunks")
    content = Column(String)
    embedding = Column(vector(1536))
    