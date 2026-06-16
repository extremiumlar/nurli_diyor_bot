"""
Mavjud applications jadvaliga yangi ustunlarni qo'shadi.
SQLite va PostgreSQL ikkalasiga ham mos.
Bir necha marta ishga tushirilsa ham xavfsiz.
"""
import asyncio
from sqlalchemy import text
from app.database.connect import engine


COLUMNS_TO_ADD = [
    ("address",           "VARCHAR(256)"),
    ("birth_year",        "VARCHAR(10)"),
    ("education",         "VARCHAR(128)"),
    ("age",               "INTEGER"),
    ("languages",         "VARCHAR(256)"),
    ("additional_skills", "TEXT"),
]


async def main():
    async with engine.begin() as conn:
        result = await conn.execute(text("PRAGMA table_info(applications)"))
        existing = {row[1] for row in result.fetchall()} if engine.dialect.name == "sqlite" else None

        if existing is None:
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'applications'"
            ))
            existing = {row[0] for row in result.fetchall()}

        for name, col_type in COLUMNS_TO_ADD:
            if name in existing:
                print(f"SKIP: {name} (mavjud)")
                continue
            sql = f"ALTER TABLE applications ADD COLUMN {name} {col_type}"
            await conn.execute(text(sql))
            print(f"OK: {sql}")

    print("Migratsiya muvaffaqiyatli tugadi!")


if __name__ == "__main__":
    asyncio.run(main())
