from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
from app.core.database import get_db
from app.modules.users.model import User
from app.core.dependencies import get_current_user

from app.modules.users.schemas import (
    UserUpdateRequest, UserRoleUpdateRequest,
    UserResponse
)


router = APIRouter(prefix="/users", tags=["Users"])

#Get Current User Profile
@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get the currently logged-in user's profile.
    (Requires JWT implementation)
    """
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(user_update: UserUpdateRequest):
    """
    Update the currently logged-in user's details.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet. Wait for Day 4.")
    
#Logout
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    #remove the token
    current_user.refresh_token_hash = None
    current_user.refresh_token_exp = None
    await db.commit()
    return {"message": "Logged out successfully"}   
