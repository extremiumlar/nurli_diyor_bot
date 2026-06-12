"""
Mavjud applications jadvaliga yangi ustunlar qo'shadi.
Faqat bir marta ishga tushirish kerak.
"""
import asyncio
from sqlalchemy import text
from app.database.connect import engine


async def main():
    migrations = [
        "ALTER TABLE applications ADD COLUMN IF NOT EXISTS address    VARCHAR(256)",
        "ALTER TABLE applications ADD COLUMN IF NOT EXISTS birth_year  VARCHAR(10)",
        "ALTER TABLE applications ADD COLUMN IF NOT EXISTS education   VARCHAR(128)",
    ]
    async with engine.begin() as conn:
        for sql in migrations:
            await conn.execute(text(sql))
            print(f"OK: {sql}")

    print("Migratsiya muvaffaqiyatli tugadi!")


if __name__ == "__main__":
    asyncio.run(main())
