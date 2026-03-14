from pydantic import BaseModel, UUID4, ConfigDict
from typing import Any
from app.common.enums import ReviewStatus

class ReviewResponse(BaseModel):
    id: UUID4
    repository_id: UUID4
    status: ReviewStatus
    quality_score: int | None = None
    security_score: int | None = None
    maintainability_score: int | None = None
    summary: str | None = None
    top_issues: Any | None = None 

    # The modern Pydantic v2 configuration
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)