from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
from app.core.database import get_db
from app.modules.user.model import User
from app.core.dependencies import get_current_user

from app.modules.user.schema import (
    UserUpdateRequest, UserRoleUpdateRequest,
    UserResponse
)


from app.modules.user import service as user_service

router = APIRouter(tags=["Users"])

#Get Current User Profile
@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get the currently logged-in user's profile.
    """
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the currently logged-in user's details.
    """
    try:
        return await user_service.update_profile(db, current_user, user_update)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


#Logout
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await user_service.logout(db, current_user)
    return {"message": "Logged out successfully"}   
