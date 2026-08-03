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

SQLite va PostgreSQL ikkalasiga mos. Bir necha marta ishga tushirilsa ham
xavfsiz (ikkinchi safar o'zgartiradigan narsa qolmaydi).

Ishga tushirish (virtualenv AKTIV holatda):
    source /home/bulutlii/virtualenv/nurli_diyor_bot/3.11/bin/activate
    cd /home/bulutlii/nurli_diyor_bot && python migrate_v4.py
"""
import asyncio
from sqlalchemy import select, func, update as sql_update
from app.database.connect import engine, async_session
from app.database.models import Application, ApplicationAnswer


async def main():
    print(f"Dialekt: {engine.dialect.name}")
    async with async_session() as s:
        # 1) Saralash davri qachon boshlangan?
        res = await s.execute(
            select(func.min(Application.created_at))
            .where(Application.id.in_(select(ApplicationAnswer.application_id).distinct()))
        )
        cutoff = res.scalar()

        # 2) Tuzatishga nomzod arizalar
        q = select(Application).where(Application.status == "in_progress")
        if cutoff is not None:
            q = q.where(Application.created_at < cutoff)
            print(f"Saralash davri boshlanishi: {cutoff}")
            print("Shu vaqtdan OLDIN yaratilgan tugatilmagan arizalar tuzatiladi.")
        else:
            print("Hali saralashdan o'tgan ariza yo'q —")
            print("barcha 'in_progress' arizalar eski deb hisoblanadi.")

        res = await s.execute(q)
        olds = res.scalars().all()

        if not olds:
            print("\n✅ Tuzatishga ariza yo'q — hammasi joyida.")
            await engine.dispose()
            return

        # 3) Javobi bor arizalarga TEGMAYMIZ (ular yangi oqimdan)
        res = await s.execute(select(ApplicationAnswer.application_id).distinct())
        with_answers = set(res.scalars().all())
        targets = [a for a in olds if a.id not in with_answers]
        skipped = len(olds) - len(targets)

        print(f"\nTopildi: {len(olds)} ta 'in_progress' ariza")
        if skipped:
            print(f"  ⏭  {skipped} tasiga tegilmadi (javoblari bor — yangi oqimdan)")
        print(f"  ✏️  {len(targets)} tasi tuzatiladi")

        if not targets:
            print("\n✅ Tuzatishga ariza qolmadi.")
            await engine.dispose()
            return

        for a in targets[:10]:
            print(f"     #{a.id:<5} {(a.full_name or '—')[:28]:<28} {a.created_at}")
        if len(targets) > 10:
            print(f"     … va yana {len(targets) - 10} ta")

        await s.execute(
            sql_update(Application)
            .where(Application.id.in_([a.id for a in targets]))
            .values(status="submitted", stage="done")
        )
        await s.commit()
        print(f"\n✅ {len(targets)} ta eski ariza tuzatildi (status=submitted, stage=done).")
        print("   Endi ular Excel hisobotida va HR ro'yxatlarida ko'rinadi.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
