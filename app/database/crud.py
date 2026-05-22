from sqlalchemy import select
from app.database.connect import async_session
from app.database.models import User

async def get_user(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

async def create_or_update_user(user_id: int, username: str | None, full_name: str | None):
    async with async_session() as session:
        user = await session.get(User, user_id)

        if user:
            user.username = username
            user.full_name = full_name
        else:
            user = User(
                id=user_id,
                username=username,
                full_name=full_name
            )
            session.add(user)

        await session.commit()
        return user

async def update_user_role(user_id: int, role: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.role = role
            await session.commit()