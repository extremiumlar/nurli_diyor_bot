"""
Saralash bosqichlarini boshqarish uchun migratsiya.

Qo'shiladigan ustunlar:
  vacancies.questions_enabled — test va yozma savollar yoqilganmi (default: ha)
  vacancies.video_mode        — required | optional | off (default: required)
  applications.max_total      — ariza necha balldan baholangani (19, 15, 4...)

Mavjud arizalarga `max_total = 19` yoziladi (avvalgi tizim shunday edi).

SQLite va PostgreSQL ikkalasiga mos, idempotent.

Ishga tushirish (virtualenv AKTIV holatda):
    source /home/bulutlii/virtualenv/nurli_diyor_bot/3.11/bin/activate
    cd /home/bulutlii/nurli_diyor_bot && python migrate_v5.py
"""
import asyncio
from sqlalchemy import text
from app.database.connect import engine

COLUMNS = {
    "vacancies": [
        ("questions_enabled", "BOOLEAN"),
        ("video_mode", "VARCHAR(10)"),
    ],
    "applications": [
        ("max_total", "INTEGER"),
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
                await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}"))
                print(f"OK: {table}.{name} qo'shildi")

        # Standart qiymatlar (eski yozuvlar uchun)
        r = await conn.execute(text(
            "UPDATE vacancies SET questions_enabled = 1 WHERE questions_enabled IS NULL"))
        if r.rowcount:
            print(f"OK: {r.rowcount} ta vakansiyaga questions_enabled = ha")
        r = await conn.execute(text(
            "UPDATE vacancies SET video_mode = 'required' WHERE video_mode IS NULL"))
        if r.rowcount:
            print(f"OK: {r.rowcount} ta vakansiyaga video_mode = majburiy")
        r = await conn.execute(text(
            "UPDATE applications SET max_total = 19 WHERE max_total IS NULL"))
        if r.rowcount:
            print(f"OK: {r.rowcount} ta arizaga max_total = 19")

    print("migrate_v5 muvaffaqiyatli tugadi!")


if __name__ == "__main__":
    asyncio.run(main())
