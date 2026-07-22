"""
Saralash tizimi (2/3-bosqich) uchun migratsiya.
Mavjud `applications` va `vacancies` jadvallariga yangi ustunlar qo'shadi.
Yangi jadvallar (vacancy_questions, application_answers) startup'da
create_all orqali avtomatik yaratiladi.

SQLite va PostgreSQL ikkalasiga ham mos (dialekt avtomatik aniqlanadi).
Bir necha marta ishga tushirilsa ham xavfsiz (mavjud ustunlar o'tkazib yuboriladi).

Ishga tushirish (serverda, restart'dan OLDIN):
    source /home/bulutlii/virtualenv/nurli_diyor_bot/3.11/bin/activate
    cd /home/bulutlii/nurli_diyor_bot && python migrate_v2.py
"""
import asyncio
from sqlalchemy import text
from app.database.connect import engine


def _columns(dialect: str):
    is_pg = dialect == "postgresql"
    dt = "TIMESTAMP" if is_pg else "DATETIME"      # Postgres'da DATETIME yo'q
    # Boolean uchun DB default qo'ymaymiz — ORM default=False yangi qatorlarni hal qiladi,
    # eski qatorlar NULL (falsy) bo'lib qoladi. Bu ikkala dialektda ham xavfsiz.
    return {
        "applications": [
            ("expected_salary", "VARCHAR(64)"),
            ("stage",           "VARCHAR(12) DEFAULT 'stage1'"),
            ("status",          "VARCHAR(12) DEFAULT 'in_progress'"),
            ("test_score",      "INTEGER"),
            ("written_score",   "INTEGER"),
            ("video_score",     "INTEGER"),
            ("total_score",     "INTEGER"),
            ("video_file_id",   "VARCHAR(256)"),
            ("video_is_note",   "BOOLEAN"),
            ("hr_note",         "TEXT"),
            ("reviewed_by",     "BIGINT"),
            ("reviewed_at",     dt),
        ],
        "vacancies": [
            ("salary_ceiling", "INTEGER"),
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


async def _add_columns(conn, table: str, columns: list):
    existing = await _existing_columns(conn, table)
    for name, col_type in columns:
        if name in existing:
            print(f"SKIP: {table}.{name} (mavjud)")
            continue
        sql = f"ALTER TABLE {table} ADD COLUMN {name} {col_type}"
        await conn.execute(text(sql))
        print(f"OK: {sql}")


async def main():
    cols = _columns(engine.dialect.name)
    print(f"Dialekt: {engine.dialect.name}")
    async with engine.begin() as conn:
        for table, columns in cols.items():
            await _add_columns(conn, table, columns)
    print("migrate_v2 muvaffaqiyatli tugadi!")


if __name__ == "__main__":
    asyncio.run(main())
