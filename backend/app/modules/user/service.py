from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.user.model import User
from app.modules.user.schema import UserUpdateRequest

async def update_profile(db: AsyncSession, user: User, user_update: UserUpdateRequest) -> User:
    if user_update.full_name:
        user.full_name = user_update.full_name
    
    await db.commit()
    await db.refresh(user)
    return user

async def logout(db: AsyncSession, user: User) -> None:
    user.refresh_token_hash = None
    user.refresh_token_exp = None
    await db.commit()
