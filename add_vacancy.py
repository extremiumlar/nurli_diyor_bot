"""
Terminaldan vakansiya qo'shish (savollari bilan birga).

Vakansiyani bazaga yozadi va nomiga mos savol shablonini avtomatik
biriktiradi (3 test + 2 yozma + 1 video-savol).

Foydalanish:
    python add_vacancy.py "Nomi" ["Talablar"] ["Ish haqi"]

Misollar:
    python add_vacancy.py "Loyihachi (Arxitektor-loyihachi)"
    python add_vacancy.py "Elektrik" "PUE bilishi, 3 yil tajriba" "8 000 000"

Mavjud vakansiyalarni ko'rish:
    python add_vacancy.py --list
"""
import asyncio
import sys

from app.database.connect import engine, Base
from app.database import models  # noqa: F401 — jadvallar ro'yxatga olinishi uchun
import app.database.crud as crud
from app.question_bank import match_bank_key, QUESTION_BANK

# Hujjatdan olingan tayyor matnlar (nomi mos kelsa avtomatik qo'yiladi)
PRESETS = {
    "loyihachi": (
        "Bino va inshootlarning arxitektura-qurilish loyiha hujjatlari va "
        "chizmalarini ishlab chiqish, ularning me'yorlarga (ShNQ, GOST) va TZ ga "
        "muvofiqligini ta'minlash.\n\n"
        "Talablar: AutoCAD / Revit / ArchiCAD va BIM bilan ishlash, qurilish "
        "normalarini bilish, konstruktiv va muhandislik bo'limlari bilan "
        "muvofiqlashtira olish."
    ),
}


async def show_list():
    vacancies = await crud.get_all_vacancies()
    if not vacancies:
        print("Vakansiya yo'q.")
        return
    print(f"\nJami {len(vacancies)} ta vakansiya:\n")
    for v in vacancies:
        n = await crud.count_vacancy_questions(v.id)
        mark = "🟢" if v.active else "🔴"
        q = f"{n} savol" if n else "SAVOL YO'Q"
        print(f"  {mark} #{v.id:<3} {v.title:<38} {q}")
    print()


async def main():
    args = [a for a in sys.argv[1:] if a.strip()]

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if not args or args[0] in ("--list", "-l"):
        await show_list()
        await engine.dispose()
        return

    title = args[0].strip()
    requirements = args[1].strip() if len(args) > 1 else None
    salary = args[2].strip() if len(args) > 2 else None

    # Takrorlanmasligini tekshiramiz
    existing = await crud.get_all_vacancies()
    dup = next((v for v in existing if v.title.strip().lower() == title.lower()), None)
    if dup:
        n = await crud.count_vacancy_questions(dup.id)
        print(f"\n⚠️  Bunday vakansiya allaqachon bor: #{dup.id} «{dup.title}» ({n} savol)")
        print("   Nomini o'zgartiring yoki botdan tahrirlang.\n")
        await engine.dispose()
        return

    key = match_bank_key(title)
    if requirements is None and key in PRESETS:
        requirements = PRESETS[key]

    v = await crud.create_vacancy(title, requirements or "—", salary)
    print(f"\n✅ Vakansiya yaratildi: #{v.id} «{v.title}»")

    if key:
        n = await crud.set_questions_from_bank(v.id, key)
        print(f"🤖 Savollar biriktirildi: {QUESTION_BANK[key]['title']} — {n} ta")
        print("   (3 test + 2 yozma + 1 majburiy video-savol)")
    else:
        print("⚠️  Mos savol shabloni topilmadi.")
        print("   Botdan qo'shing: /admin → Vakansiyalar → vakansiya → 📝 Savollar")
        print("   → 🤖 AI bilan yaratish")

    print("\nBot menyusida darhol ko'rinadi — restart shart emas.\n")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
