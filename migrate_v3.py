"""
AI baholash uchun migratsiya (applications.ai_summary ustuni).

SQLite va PostgreSQL ikkalasiga ham mos. Bir necha marta ishga tushirilsa ham
xavfsiz (mavjud ustun o'tkazib yuboriladi).

Ishga tushirish (virtualenv AKTIV holatda):
    source /home/bulutlii/virtualenv/nurli_diyor_bot/3.11/bin/activate
    cd /home/bulutlii/nurli_diyor_bot && python migrate_v3.py
"""
import asyncio
from sqlalchemy import text
from app.database.connect import engine

COLUMNS = {
    "applications": [
        ("ai_summary", "TEXT"),
    ],
}


async def _existing_columns(conn, table: str) -> set:
    if engine.dialect.name == "sqlite":
        result = await conn.execute(text(f"PRAGMA table_info({table})"))
        return {row[1] for row in result.fetchall()}
    result = await conn.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name = :t"
    ), {"t": table})
    return {row[0] for row in result.fetchall()}


async def main():
    print(f"Dialekt: {engine.dialect.name}")
    async with engine.begin() as conn:
        for table, cols in COLUMNS.items():
            existing = await _existing_columns(conn, table)
            for name, col_type in cols:
                if name in existing:
                    print(f"SKIP: {table}.{name} (mavjud)")
                    continue
                sql = f"ALTER TABLE {table} ADD COLUMN {name} {col_type}"
                await conn.execute(text(sql))
                print(f"OK: {sql}")
    print("migrate_v3 muvaffaqiyatli tugadi!")


if __name__ == "__main__":
    asyncio.run(main())
