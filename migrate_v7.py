"""
Dublikat javoblarni tozalash + "1 savol = 1 javob" cheklovini o'rnatish (R1).

Muammo (tahlil/C2.md): application_answers da UNIQUE yo'q — tugmani ikki
marta bosish yoki ikki worker poygasi bitta savolga ikkita javob yozadi,
ball 9 dan oshib ketadi. Handler'dagi tekshiruv check-then-act — atomik emas.

Bu migratsiya:
  1. (application_id, question_id) bo'yicha dublikatlarni o'chiradi.
     Qoldirish qoidasi: baholangani (score IS NOT NULL) afzal, teng bo'lsa
     eng birinchi yozilgani (MIN id) — nomzod foydasiga.
  2. Ta'sirlangan arizalarning ballarini qayta hisoblaydi
     (crud.recompute_scores mantig'i bilan bir xil, lekin xom SQL'da).
  3. Partial UNIQUE indeks quradi — bundan keyin DB o'zi dublikatni to'sadi.

SQLite va PostgreSQL ikkalasiga mos, idempotent (qayta ishlatish xavfsiz).
Faqat xom SQL — ORM modellariga bog'lanmaydi.

Ishga tushirish (virtualenv AKTIV holatda):
    source /home/bulutlii/virtualenv/nurli_diyor_bot/3.11/bin/activate
    cd /home/bulutlii/nurli_diyor_bot && python migrate_v7.py
"""
import asyncio
from sqlalchemy import text
from app.database.connect import engine

# question_bank.STAGE_ON bilan bir xil — bosqich hisobga kiradigan rejimlar.
# Ataylab nusxa: migratsiya app modullariga minimal bog'lanadi.
STAGE_ON = ("required", "optional")


async def _dedup(conn) -> list[int]:
    """Dublikatlarni o'chiradi, ta'sirlangan application_id ro'yxatini beradi."""
    groups = (await conn.execute(text(
        "SELECT application_id, question_id, COUNT(*) AS c "
        "FROM application_answers "
        "WHERE question_id IS NOT NULL "
        "GROUP BY application_id, question_id HAVING COUNT(*) > 1"
    ))).fetchall()

    if not groups:
        print("OK: dublikat javob yo'q")
        return []

    affected = []
    removed_total = 0
    for app_id, q_id, cnt in groups:
        rows = (await conn.execute(text(
            "SELECT id, score FROM application_answers "
            "WHERE application_id = :a AND question_id = :q ORDER BY id"
        ), {"a": app_id, "q": q_id})).fetchall()

        # Qoldiramiz: baholangani afzal, teng bo'lsa eng kichik id
        keep = min(rows, key=lambda r: (r[1] is None, r[0]))[0]
        drop = [r[0] for r in rows if r[0] != keep]

        for did in drop:
            await conn.execute(text(
                "DELETE FROM application_answers WHERE id = :i"), {"i": did})
        removed_total += len(drop)
        affected.append(app_id)
        print(f"  ✏️ Ariza #{app_id}, savol #{q_id}: {cnt} ta javob -> 1 ta "
              f"(qoldi id={keep}, o'chdi {len(drop)} ta)")

    print(f"OK: {removed_total} ta dublikat javob o'chirildi "
          f"({len(set(affected))} ta arizada)")
    return sorted(set(affected))


async def _recompute(conn, app_ids: list[int]):
    """Ta'sirlangan arizalar ballarini qayta hisoblaydi.

    crud.recompute_scores bilan bir xil semantika:
      - test_score: barcha test javoblari yig'indisi (score NULL -> 0)
      - written_score: FAQAT hamma yozma javob baholangan bo'lsa yig'indi;
        aks holda TEGILMAYDI (baholanmagan javobni 0 qilib yubormaslik uchun)
      - total_score: qo'llaniladigan bosqichlar to'liq bo'lsagina yig'iladi
    """
    for app_id in app_ids:
        answers = (await conn.execute(text(
            "SELECT qtype, score FROM application_answers "
            "WHERE application_id = :a"), {"a": app_id})).fetchall()
        tests = [s for (t, s) in answers if t == "test"]
        written = [s for (t, s) in answers if t == "written"]

        app_row = (await conn.execute(text(
            "SELECT vacancy_id, video_score, test_score, written_score "
            "FROM applications WHERE id = :a"), {"a": app_id})).fetchone()
        if app_row is None:
            continue
        vacancy_id, video_score, old_test, old_written = app_row

        test_score = sum((s or 0) for s in tests) if tests else old_test
        if written and all(s is not None for s in written):
            written_score = sum(written)
        else:
            written_score = old_written  # tegilmaydi

        # Vakansiya rejimlari — total uchun
        q_mode, v_mode = "required", "required"
        if vacancy_id is not None:
            vac = (await conn.execute(text(
                "SELECT questions_mode, video_mode FROM vacancies "
                "WHERE id = :v"), {"v": vacancy_id})).fetchone()
            if vac:
                q_mode = vac[0] or "required"
                v_mode = vac[1] or "required"

        parts, ready = 0, True
        if q_mode in STAGE_ON:
            if test_score is None or written_score is None:
                ready = False
            else:
                parts += test_score + written_score
        if v_mode in STAGE_ON:
            if video_score is None:
                ready = False
            else:
                parts += video_score
        total = parts if ready else None

        await conn.execute(text(
            "UPDATE applications SET test_score = :t, written_score = :w, "
            "total_score = :tot WHERE id = :a"),
            {"t": test_score, "w": written_score, "tot": total, "a": app_id})
        print(f"  ✅ Ariza #{app_id}: test={test_score} yozma={written_score} "
              f"jami={total}")


async def _index_exists(conn, name: str) -> bool:
    if engine.dialect.name == "sqlite":
        r = await conn.execute(text(
            "SELECT 1 FROM sqlite_master WHERE type='index' AND name=:n"),
            {"n": name})
    else:
        r = await conn.execute(text(
            "SELECT 1 FROM pg_indexes WHERE indexname = :n"), {"n": name})
    return r.fetchone() is not None


async def main():
    print(f"Dialekt: {engine.dialect.name}")
    async with engine.begin() as conn:
        # 1) Dublikatlarni tozalash
        affected = await _dedup(conn)

        # 2) Ta'sirlangan arizalarni qayta hisoblash
        if affected:
            print(f"Ballarni qayta hisoblash ({len(affected)} ta ariza):")
            await _recompute(conn, affected)

        # 3) Partial UNIQUE indeks
        if await _index_exists(conn, "uq_answer_app_question"):
            print("SKIP: uq_answer_app_question (mavjud)")
        else:
            await conn.execute(text(
                "CREATE UNIQUE INDEX uq_answer_app_question "
                "ON application_answers (application_id, question_id) "
                "WHERE question_id IS NOT NULL"))
            print("OK: uq_answer_app_question indeksi qurildi — "
                  "endi DB dublikat javobni o'zi to'sadi")

    print("migrate_v7 muvaffaqiyatli tugadi!")


if __name__ == "__main__":
    asyncio.run(main())
