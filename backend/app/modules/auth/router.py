from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_db
from app.modules.auth.schemas import UserRegisterRequest, RefreshTokenRequest, TokenResponse
from app.modules.users.schemas import UserResponse 
from app.modules.auth import service as auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    """
    return await auth_service.register_user(db, user_in)

@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Login user and return tokens.
    """
    user = await auth_service.authenticate_user(db, form_data.username, form_data.password)
    return await auth_service.login_user(db, user)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_token_in: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    return await auth_service.refresh_token(db, refresh_token_in)
