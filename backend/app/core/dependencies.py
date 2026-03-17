from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.database import get_db
from app.modules.user.model import User

# ─── 1. THE SWAGGER UI CONNECTOR ──────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


# ─── 2. DEPENDENCY ──────────────────────────────
async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> User:
    
    # Pre-define the error we will throw if anything looks suspicious
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Step A: Cryptographic Verification
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        # Step B: Data Extraction
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        # Step C: The Logical Security Gate
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        # Catches expired tokens, forged signatures, or complete garbage strings
        raise credentials_exception

    # Step D: Database Verification
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # Step E: Does the user still exist?
    if user is None or not user.is_active:
        raise credentials_exception
        
    return user