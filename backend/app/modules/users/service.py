from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User
from app.modules.users.schemas import UserUpdateRequest

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
