"""
Saralash tizimi holatini tekshiradi (diagnostika).
Ishga tushirish (virtualenv aktiv holatda):
    source /home/bulutlii/virtualenv/nurli_diyor_bot/3.11/bin/activate
    cd /home/bulutlii/nurli_diyor_bot
    python check_screening.py 2>&1 | grep -Ev "INFO sqlalchemy"
"""
import asyncio
from sqlalchemy import text
from app.database.connect import engine
import app.database.crud as crud


async def main():
    print("=" * 50)
    print("Dialekt (baza turi):", engine.dialect.name)

    async with engine.begin() as conn:
        if engine.dialect.name == "sqlite":
            r = await conn.execute(text("PRAGMA table_info(applications)"))
            cols = {row[1] for row in r.fetchall()}
        else:
            r = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='applications'"))
            cols = {row[0] for row in r.fetchall()}

    need = ["expected_salary", "stage", "status", "test_score",
            "written_score", "video_score", "total_score", "video_file_id"]
    print("\napplications jadvali — saralash ustunlari:")
    missing = 0
    for c in need:
        ok = c in cols
        if not ok:
            missing += 1
        print(f"  {c:16s}: {'BOR ✅' if ok else 'YO`Q ❌'}")

    if missing:
        print(f"\n⚠️  {missing} ta ustun yo'q! migrate_v2.py ishlamagan.")
        print("   Yechim: python migrate_v2.py (virtualenv aktiv holatda) -> Restart")
    else:
        print("\n✅ Barcha ustun bor — migratsiya bajarilgan.")

    print("\n" + "=" * 50)
    vacs = await crud.get_all_vacancies()
    print(f"Vakansiyalar ({len(vacs)}) va biriktirilgan savollar:")
    for v in vacs:
        n = await crud.count_vacancy_questions(v.id)
        mark = "✅" if n > 0 else "❌ savol yo'q"
        print(f"  #{v.id}  {v.title}: {n} savol  {mark}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
