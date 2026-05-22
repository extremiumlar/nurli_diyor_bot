import asyncio
from app.database.connect import engine, Base
from app.database import models

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Jadvallar yaratildi")

if __name__ == "__main__":
    asyncio.run(main())