from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from app.common.enums import UserRole

class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(None, max_length=255)

class UserRoleUpdateRequest(BaseModel):
    role: UserRole

#Response Models

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None = Field(None, max_length=255)
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class OAuthCallbackResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int