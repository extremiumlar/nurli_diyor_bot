# -*- coding: utf-8 -*-
"""Saralash tizimi — admin tomoni: vakansiyaga savol biriktirish va
HR panel (reyting, yozma/video baholash, tasdiqlash/rad etish)."""
import re
from datetime import datetime

from aiogram import Router, Bot
from aiogram.types import CallbackQuery

from app.database.crud import (
    get_vacancy, get_all_vacancies, get_application, get_application_answers,
    count_vacancy_questions, set_questions_from_bank, delete_vacancy_questions,
    update_answer_score, recompute_scores, update_application, get_user,
    get_ranked_applications, get_screening_counts,
)
from app.keyboards.inline import (
    vacancy_questions_menu_keyboard, question_templates_keyboard,
    screening_vacancies_keyboard, candidate_list_keyboard, candidate_card_keyboard,
    grade_written_keyboard, grade_video_keyboard,
)
from app.question_bank import color_for, MAX_TEST, MAX_WRITTEN, MAX_VIDEO, MAX_TOTAL
from app.handlers.admin import get_role, is_hr

router = Router()

STATUS_LABEL = {
    "submitted":   "🕐 Ko'rib chiqilmoqda",
    "approved":    "✅ Tasdiqlangan",
    "rejected":    "❌ Rad etilgan",
    "in_progress": "⏳ Tugatilmagan",
}


async def _guard(callback: CallbackQuery) -> bool:
    role = await get_role(callback.from_user.id)
    if not is_hr(role):
        await callback.answer("❌ Ruxsat yo'q.")
        return False
    return True


# ══════════════════════════════════════════════════════════════════════════
#  Vakansiya savollarini biriktirish
# ══════════════════════════════════════════════════════════════════════════

@router.callback_query(lambda c: c.data.startswith("vq:menu:"))
async def vq_menu(callback: CallbackQuery):
    if not await _guard(callback):
        return
    vid = int(callback.data.split(":")[2])
    v = await get_vacancy(vid)
    if not v:
        await callback.answer("Vakansiya topilmadi.", show_alert=True)
        return
    n = await count_vacancy_questions(vid)
    text = (
        f"📝 <b>{v.title}</b> — saralash savollari\n\n"
        f"Hozir biriktirilgan savollar: <b>{n} ta</b>\n\n"
        + ("Savollar bor — nomzodlar 2-bosqichdan (test + yozma) o'tadi.\n"
           if n else
           "Savol yo'q — bu vakansiyaga faqat oddiy ariza (1-bosqich) olinadi.\n")
        + "\nSavol biriktirish uchun tayyor shablonni tanlang."
    )
    await callback.message.answer(text, parse_mode="HTML",
                                  reply_markup=vacancy_questions_menu_keyboard(vid, n > 0))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vq:tmpl:"))
async def vq_templates(callback: CallbackQuery):
    if not await _guard(callback):
        return
    vid = int(callback.data.split(":")[2])
    await callback.message.answer(
        "📋 <b>Shablonni tanlang</b>\n\n"
        "Tanlangan lavozim savollari (3 test + 2 yozma) shu vakansiyaga nusxalanadi. "
        "Mavjud savollar almashtiriladi.",
        parse_mode="HTML",
        reply_markup=question_templates_keyboard(vid)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vq:set:"))
async def vq_set(callback: CallbackQuery):
    if not await _guard(callback):
        return
    parts = callback.data.split(":")
    vid = int(parts[2])
    key = parts[3]
    n = await set_questions_from_bank(vid, key)
    if n == 0:
        await callback.answer("Shablon topilmadi.", show_alert=True)
        return
    v = await get_vacancy(vid)
    await callback.message.answer(
        f"✅ <b>{v.title}</b> vakansiyasiga {n} ta savol biriktirildi "
        f"(3 test + 2 yozma).\n\nEndi bu vakansiyaga kelgan nomzodlar to'liq "
        f"saralashdan o'tadi.",
        parse_mode="HTML",
        reply_markup=vacancy_questions_menu_keyboard(vid, True)
    )
    await callback.answer("Biriktirildi ✅")


@router.callback_query(lambda c: c.data.startswith("vq:clear:"))
async def vq_clear(callback: CallbackQuery):
    if not await _guard(callback):
        return
    vid = int(callback.data.split(":")[2])
    await delete_vacancy_questions(vid)
    await callback.message.answer(
        "🗑 Savollar o'chirildi. Endi bu vakansiyaga faqat oddiy ariza olinadi.",
        reply_markup=vacancy_questions_menu_keyboard(vid, False)
    )
    await callback.answer("O'chirildi")


# ══════════════════════════════════════════════════════════════════════════
#  HR panel — reyting va baholash
# ══════════════════════════════════════════════════════════════════════════

def _fmt(v, mx):
    return f"{v}/{mx}" if v is not None else f"—/{mx}"


def _card_text(app, vacancy, answers) -> str:
    written = [a for a in answers if a.qtype == "written"]
    name = app.full_name or app.user_id
    name_link = f'<a href="tg://user?id={app.user_id}">{name}</a>'
    total = app.total_score
    color = color_for(total) if total is not None else "⚪️"

    salary_flag = ""
    if vacancy and vacancy.salary_ceiling and app.expected_salary:
        digits = re.sub(r"[^\d]", "", app.expected_salary)
        if digits and int(digits) > vacancy.salary_ceiling:
            salary_flag = " 💰 (shiftdan yuqori)"

    lines = [
        f"{color} <b>Nomzod #{app.id}</b> · {STATUS_LABEL.get(app.status, app.status)}",
        f"👤 {name_link}",
        f"📱 {app.phone or '—'}",
        f"💼 {vacancy.title if vacancy else '—'}",
        f"💰 Kutgan maosh: {app.expected_salary or '—'}{salary_flag}",
        "",
        f"🧪 Test: <b>{_fmt(app.test_score, MAX_TEST)}</b>   "
        f"✍️ Yozma: <b>{_fmt(app.written_score, MAX_WRITTEN)}</b>   "
        f"🎬 Video: <b>{_fmt(app.video_score, MAX_VIDEO)}</b>",
        f"⭐️ <b>Jami: {_fmt(app.total_score, MAX_TOTAL)}</b>",
        "",
        "<b>✍️ Yozma javoblar:</b>",
    ]
    if not written:
        lines.append("— yo'q")
    for i, a in enumerate(written, start=1):
        sc = f"{a.score}/3" if a.score is not None else "⚠️ baholanmagan"
        ans = (a.answer_text or "—")
        if len(ans) > 1500:
            ans = ans[:1500] + "…"
        lines.append(f"\n<b>{i}.</b> {a.question_text or '—'}\n<i>{ans}</i>\n➡️ {sc}")
    return "\n".join(lines)


async def _render_card(callback: CallbackQuery, app_id: int, edit: bool = True):
    app = await get_application(app_id)
    if not app:
        await callback.answer("Nomzod topilmadi.", show_alert=True)
        return
    vacancy = await get_vacancy(app.vacancy_id) if app.vacancy_id else None
    answers = await get_application_answers(app_id)
    written = [a for a in answers if a.qtype == "written"]
    kb = candidate_card_keyboard(app, written, has_video=bool(app.video_file_id))
    text = _card_text(app, vacancy, answers)
    try:
        if edit:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb,
                                             disable_web_page_preview=True)
        else:
            await callback.message.answer(text, parse_mode="HTML", reply_markup=kb,
                                          disable_web_page_preview=True)
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=kb,
                                      disable_web_page_preview=True)


@router.callback_query(lambda c: c.data == "scr:menu")
async def scr_menu(callback: CallbackQuery):
    if not await _guard(callback):
        return
    vacancies = await get_all_vacancies()
    rows = []
    for v in vacancies:
        counts = await get_screening_counts(v.id)
        total = sum(counts.values())
        if total:
            rows.append((v, total))
    if not rows:
        await callback.message.answer(
            "🎯 <b>Saralash</b>\n\nHozircha saralashdan o'tgan nomzod yo'q.\n"
            "<i>Vakansiyaga savol biriktirilgach, nomzodlar shu yerda reyting bo'yicha chiqadi.</i>",
            parse_mode="HTML"
        )
        await callback.answer()
        return
    await callback.message.answer(
        "🎯 <b>Saralash — reyting</b>\n\nVakansiyani tanlang:",
        parse_mode="HTML",
        reply_markup=screening_vacancies_keyboard(rows)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("scr:vac:"))
async def scr_vacancy(callback: CallbackQuery):
    if not await _guard(callback):
        return
    vid = int(callback.data.split(":")[2])
    v = await get_vacancy(vid)
    apps = await get_ranked_applications(vid)
    apps = [a for a in apps if a.status in ("submitted", "approved", "rejected")]
    if not apps:
        await callback.answer("Bu vakansiyada nomzod yo'q.", show_alert=True)
        return
    text = (
        f"💼 <b>{v.title if v else vid}</b> — nomzodlar reytingi\n"
        f"Jami: {len(apps)} ta. Yuqoridan pastga — balga qarab.\n\n"
        f"<i>🟢 kuchli · 🟡 o'rta · 🔴 past · ⚪️ hali baholanmagan</i>"
    )
    try:
        await callback.message.edit_text(text, parse_mode="HTML",
                                         reply_markup=candidate_list_keyboard(apps, vid))
    except Exception:
        await callback.message.answer(text, parse_mode="HTML",
                                      reply_markup=candidate_list_keyboard(apps, vid))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("scr:app:"))
async def scr_app_card(callback: CallbackQuery):
    if not await _guard(callback):
        return
    app_id = int(callback.data.split(":")[2])
    await _render_card(callback, app_id, edit=True)
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("scr:video:"))
async def scr_send_video(callback: CallbackQuery, bot: Bot):
    if not await _guard(callback):
        return
    app_id = int(callback.data.split(":")[2])
    app = await get_application(app_id)
    if not app or not app.video_file_id:
        await callback.answer("Video yo'q.", show_alert=True)
        return
    try:
        if app.video_is_note:
            await bot.send_video_note(callback.from_user.id, app.video_file_id)
        else:
            await bot.send_video(callback.from_user.id, app.video_file_id,
                                 caption=f"🎥 Nomzod #{app.id} — {app.full_name or ''}")
    except Exception as e:
        await callback.answer(f"Video yuborilmadi: {e}", show_alert=True)
        return
    await callback.answer("Video yuborildi 👆")


# ── Yozma javobni baholash ─────────────────────────────────────────────────

@router.callback_query(lambda c: c.data.startswith("scr:wgrade:"))
async def scr_written_grade(callback: CallbackQuery):
    if not await _guard(callback):
        return
    parts = callback.data.split(":")
    app_id = int(parts[2])
    answer_id = int(parts[3])
    answers = await get_application_answers(app_id)
    ans = next((a for a in answers if a.id == answer_id), None)
    if not ans:
        await callback.answer("Javob topilmadi.", show_alert=True)
        return
    text = (
        f"✍️ <b>Yozma javobni baholang (0–3)</b>\n\n"
        f"<b>Savol:</b> {ans.question_text or '—'}\n\n"
        f"<b>Javob:</b>\n<i>{(ans.answer_text or '—')[:2000]}</i>\n\n"
        f"Mezon: mavzuga aloqadorlik, mantiq/chuqurlik, aniqlik, savodxonlik."
    )
    try:
        await callback.message.edit_text(text, parse_mode="HTML",
                                         reply_markup=grade_written_keyboard(app_id, answer_id),
                                         disable_web_page_preview=True)
    except Exception:
        await callback.message.answer(text, parse_mode="HTML",
                                      reply_markup=grade_written_keyboard(app_id, answer_id))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("scr:wset:"))
async def scr_written_set(callback: CallbackQuery):
    if not await _guard(callback):
        return
    parts = callback.data.split(":")
    app_id = int(parts[2])
    answer_id = int(parts[3])
    score = int(parts[4])
    await update_answer_score(answer_id, score)
    await recompute_scores(app_id)
    await _render_card(callback, app_id, edit=True)
    await callback.answer(f"Ball: {score}/3")


# ── Video baholash ─────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data.startswith("scr:vgrade:"))
async def scr_video_grade(callback: CallbackQuery):
    if not await _guard(callback):
        return
    app_id = int(callback.data.split(":")[2])
    text = (
        "🎬 <b>Videoga ball bering (0–4)</b>\n\n"
        "Mezon: nutq va ishonch (0–2), mazmun va sohaga mosligi (0–2).\n"
        "<i>Video bo'lmasa 0 qo'ying.</i>"
    )
    try:
        await callback.message.edit_text(text, parse_mode="HTML",
                                         reply_markup=grade_video_keyboard(app_id))
    except Exception:
        await callback.message.answer(text, parse_mode="HTML",
                                      reply_markup=grade_video_keyboard(app_id))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("scr:vset:"))
async def scr_video_set(callback: CallbackQuery):
    if not await _guard(callback):
        return
    parts = callback.data.split(":")
    app_id = int(parts[2])
    score = int(parts[3])
    await update_application(app_id, video_score=score)
    await recompute_scores(app_id)
    await _render_card(callback, app_id, edit=True)
    await callback.answer(f"Video ball: {score}/4")


# ── Tasdiqlash / Rad etish ─────────────────────────────────────────────────

@router.callback_query(lambda c: c.data.startswith("scr:approve:"))
async def scr_approve(callback: CallbackQuery, bot: Bot):
    if not await _guard(callback):
        return
    app_id = int(callback.data.split(":")[2])
    app = await get_application(app_id)
    if not app:
        await callback.answer("Nomzod topilmadi.", show_alert=True)
        return
    await update_application(app_id, status="approved",
                            reviewed_by=callback.from_user.id, reviewed_at=datetime.now())
    try:
        await bot.send_message(
            app.user_id,
            "🎉 <b>Tabriklaymiz!</b> Siz suhbatga taklif qilindingiz.\n"
            "HR mutaxassisimiz qulay vaqtni kelishish uchun siz bilan bog'lanadi.",
            parse_mode="HTML"
        )
        sent = "✅ Nomzodga taklif xabari yuborildi."
    except Exception:
        sent = "⚠️ Nomzodga xabar yuborilmadi (botni bloklagan bo'lishi mumkin)."
    await _render_card(callback, app_id, edit=True)
    await callback.answer(sent, show_alert=True)


@router.callback_query(lambda c: c.data.startswith("scr:reject:"))
async def scr_reject(callback: CallbackQuery, bot: Bot):
    if not await _guard(callback):
        return
    app_id = int(callback.data.split(":")[2])
    app = await get_application(app_id)
    if not app:
        await callback.answer("Nomzod topilmadi.", show_alert=True)
        return
    await update_application(app_id, status="rejected",
                            reviewed_by=callback.from_user.id, reviewed_at=datetime.now())
    try:
        await bot.send_message(
            app.user_id,
            "Ariza uchun rahmat. Afsuski, bu vakansiya bo'yicha boshqa nomzodni tanladik.\n"
            "Ma'lumotlaringiz bazamizda saqlanadi va mos vakansiya chiqsa, siz bilan bog'lanamiz.",
        )
        sent = "✅ Nomzodga rad xabari yuborildi."
    except Exception:
        sent = "⚠️ Nomzodga xabar yuborilmadi (botni bloklagan bo'lishi mumkin)."
    await _render_card(callback, app_id, edit=True)
    await callback.answer(sent, show_alert=True)
