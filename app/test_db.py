import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:cheklanma@localhost:5432/nurli_diyor_bot"

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

async def test():
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
        print("DATABASE ULANDI")

asyncio.run(test())