from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models import User
from src.schemas.user_schema import UserCreate

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    userModel = User()
    userModel.email = user.email
    userModel.name = user.name
    
    db.add(userModel)
    await db.commit()
    await db.refresh(userModel)
    return userModel
