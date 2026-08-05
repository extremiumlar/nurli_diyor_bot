"""
ESKI ARIZALAR HOLATINI TUZATISH.

Muammo: migrate_v2.py `status` ustunini `DEFAULT 'in_progress'` bilan qo'shgan.
Shu sababli saralash tizimidan OLDIN topshirilgan barcha arizalar
«tugatilmagan» deb belgilanib qolgan — hisobotlarda noto'g'ri ko'rinadi.

Yechim: saralash tizimi ishga tushishidan OLDIN yaratilgan arizalarni
`submitted` / `done` ga o'tkazamiz.

Chegara qanday aniqlanadi (xavfsiz usul):
  Saralash davri boshlanishi = birinchi marta test/yozma javob yozilgan
  arizaning yaratilgan vaqti. Undan OLDIN yaratilgan va javobi YO'Q
  arizalar — eski, to'liq arizalar.
  Agar hali birorta saralash arizasi bo'lmasa — barcha `in_progress`
  arizalar eski hisoblanadi.

Yangi oqimda yarim tashlab ketilgan arizalarga TEGILMAYDI.

DIQQAT: bu fayl ORM modellarini ISHLATMAYDI — faqat toza SQL.
Sababi: modelda keyingi migratsiyalarda qo'shiladigan ustunlar bo'lishi
mumkin, va ular hali bazada bo'lmasa ORM so'rovi yiqiladi.

SQLite va PostgreSQL ikkalasiga mos, idempotent.

Ishga tushirish (virtualenv AKTIV holatda):
    source /home/bulutlii/virtualenv/nurli_diyor_bot/3.11/bin/activate
    cd /home/bulutlii/nurli_diyor_bot && python migrate_v4.py
"""
import asyncio
from sqlalchemy import text
from app.database.connect import engine


async def _table_exists(conn, table: str) -> bool:
    if engine.dialect.name == "sqlite":
        res = await conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:t"), {"t": table})
    else:
        res = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_name=:t"),
            {"t": table})
    return res.first() is not None


async def main():
    print(f"Dialekt: {engine.dialect.name}")
    async with engine.begin() as conn:
        for t in ("applications", "application_answers"):
            if not await _table_exists(conn, t):
                print(f"⏭  '{t}' jadvali yo'q — migratsiya kerak emas.")
                print("migrate_v4 muvaffaqiyatli tugadi!")
                return

        # 1) Saralash davri qachon boshlangan?
        res = await conn.execute(text(
            "SELECT MIN(created_at) FROM applications "
            "WHERE id IN (SELECT DISTINCT application_id FROM application_answers)"
        ))
        cutoff = res.scalar()

        params = {}
        where = "status = 'in_progress' " \
                "AND id NOT IN (SELECT DISTINCT application_id FROM application_answers)"
        if cutoff is not None:
            where += " AND created_at < :cutoff"
            params["cutoff"] = cutoff
            print(f"Saralash davri boshlanishi: {cutoff}")
            print("Shu vaqtdan OLDIN yaratilgan, javobi yo'q arizalar tuzatiladi.")
        else:
            print("Hali saralashdan o'tgan ariza yo'q —")
            print("barcha 'in_progress' arizalar eski deb hisoblanadi.")

        # 2) Nechta ariza tuzatiladi?
        res = await conn.execute(
            text(f"SELECT COUNT(*) FROM applications WHERE {where}"), params)
        n = res.scalar() or 0

        # 3) Javobi bor 'in_progress' arizalar (ularga tegilmaydi)
        res = await conn.execute(text(
            "SELECT COUNT(*) FROM applications WHERE status = 'in_progress' "
            "AND id IN (SELECT DISTINCT application_id FROM application_answers)"))
        skipped = res.scalar() or 0

        if skipped:
            print(f"  ⏭  {skipped} ta arizaga tegilmaydi (javoblari bor — yangi oqimdan)")

        if not n:
            print("\n✅ Tuzatishga ariza yo'q — hammasi joyida.")
            return

        print(f"  ✏️  {n} ta ariza tuzatiladi")

        # Namuna ko'rsatamiz
        res = await conn.execute(
            text(f"SELECT id, full_name, created_at FROM applications "
                 f"WHERE {where} ORDER BY id LIMIT 10"), params)
        for row in res.fetchall():
            name = (row[1] or "—")[:28]
            print(f"     #{row[0]:<5} {name:<28} {row[2]}")
        if n > 10:
            print(f"     … va yana {n - 10} ta")

        # 4) Tuzatamiz
        await conn.execute(
            text(f"UPDATE applications SET status = 'submitted', stage = 'done' "
                 f"WHERE {where}"), params)
        print(f"\n✅ {n} ta eski ariza tuzatildi (status=submitted, stage=done).")
        print("   Endi ular Excel hisobotida va HR ro'yxatlarida ko'rinadi.")

    print("migrate_v4 muvaffaqiyatli tugadi!")


if __name__ == "__main__":
    asyncio.run(main())
