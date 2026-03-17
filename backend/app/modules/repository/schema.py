from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.common.enums import RepoProvider, RepoStatus

#Request Models

class RepoSubmitRequest(BaseModel):

    url: str = Field(description="Full HTTPS GitHub or GitLab URL")

    is_private: bool = False
    default_branch: str = "main"

    analysis_config: dict|None = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith("https://github.com/") or v.startswith("https://gitlab.com/")):
            raise ValueError("Must be full HTTPS GitHub or GitLab URL")
        return v

class RepoUpdateRequest(BaseModel):
    default_branch: str | None = None
    analysis_config: dict | None = None

#Response Models

class RepoResponse(BaseModel):

    id: UUID
    url: str
    name: str | None = None
    provider: RepoProvider
    is_private: bool
    default_branch: str
    celery_task_id: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    status: RepoStatus

    model_config = ConfigDict(from_attributes=True)

class RepoSummaryResponse(BaseModel):
    id: UUID
    url: str
    name: str | None = None
    provider: RepoProvider
    status: RepoStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int = 0
    stage: str = ""
    result: dict | None = None
    error: str | None = None