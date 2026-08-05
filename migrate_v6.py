"""
Savollar bosqichiga uch rejim qo'shish (majburiy / ixtiyoriy / o'chirilgan).

Avval `questions_enabled` (ha/yo'q) edi — endi `questions_mode` (uch holat),
xuddi video kabi.

Eski qiymatlar o'tkaziladi:
    questions_enabled = 1  ->  questions_mode = 'required'
    questions_enabled = 0  ->  questions_mode = 'off'

SQLite va PostgreSQL ikkalasiga mos, idempotent.

Ishga tushirish (virtualenv AKTIV holatda):
    source /home/bulutlii/virtualenv/nurli_diyor_bot/3.11/bin/activate
    cd /home/bulutlii/nurli_diyor_bot && python migrate_v6.py
"""
import asyncio
from sqlalchemy import text
from app.database.connect import engine


async def _columns(conn, table: str) -> set:
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
        cols = await _columns(conn, "vacancies")

        if "questions_mode" in cols:
            print("SKIP: vacancies.questions_mode (mavjud)")
        else:
            await conn.execute(text(
                "ALTER TABLE vacancies ADD COLUMN questions_mode VARCHAR(10)"))
            print("OK: vacancies.questions_mode qo'shildi")

        # Eski ustundan qiymatlarni o'tkazamiz
        if "questions_enabled" in cols:
            r = await conn.execute(text(
                "UPDATE vacancies SET questions_mode = "
                "CASE WHEN questions_enabled = 0 THEN 'off' ELSE 'required' END "
                "WHERE questions_mode IS NULL"))
            if r.rowcount:
                print(f"OK: {r.rowcount} ta vakansiyaga eski sozlama o'tkazildi")
        else:
            r = await conn.execute(text(
                "UPDATE vacancies SET questions_mode = 'required' "
                "WHERE questions_mode IS NULL"))
            if r.rowcount:
                print(f"OK: {r.rowcount} ta vakansiyaga questions_mode = majburiy")

        # Ehtiyot: video_mode ham to'ldirilgan bo'lsin
        r = await conn.execute(text(
            "UPDATE vacancies SET video_mode = 'required' WHERE video_mode IS NULL"))
        if r.rowcount:
            print(f"OK: {r.rowcount} ta vakansiyaga video_mode = majburiy")

    print("migrate_v6 muvaffaqiyatli tugadi!")


if __name__ == "__main__":
    asyncio.run(main())
