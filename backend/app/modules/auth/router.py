from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.modules.users.model import User 
from app.modules.auth.schemas import UserRegisterRequest, UserLoginRequest, RefreshTokenRequest, TokenResponse
from app.modules.users.schemas import UserResponse 

router = APIRouter(prefix="/auth", tags=["Authentication"])




@router.post("/register", response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    new_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password)
    )    
    
    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database transaction failed."
        )
    
    return new_user
    

@router.post("/login", response_model=TokenResponse)
async def login_user(user_in: UserLoginRequest, db: AsyncSession = Depends(get_db)):

    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    user = result.scalars().first()

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user or not user.is_active or not user.hashed_password or not verify_password(user_in.password, user.hashed_password):
        raise credential_exception

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    user.refresh_token_hash = get_password_hash(refresh_token)
    user.refresh_token_exp = datetime.now(timezone.utc) + timedelta(days=7)
    user.last_login = datetime.now(timezone.utc)
    
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_token_in: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    credentials_exeception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(refresh_token_in.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if not user_id or token_type != "refresh":
            raise credentials_exeception
    except JWTError:
        raise credentials_exeception

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not user.refresh_token_hash:
        raise credentials_exeception

    if user.refresh_token_exp < datetime.now(timezone.utc):
        raise credentials_exception

    if not verify_password(refresh_token_in.refresh_token, user.refresh_token_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token reuse detected. All sessions revoked. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    new_access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))

    user.refresh_token_hash = get_password_hash(new_refresh_token)
    user.refresh_token_exp = datetime.now(timezone.utc) + timedelta(days=7)
    user.last_login = datetime.now(timezone.utc)
        
    await db.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
