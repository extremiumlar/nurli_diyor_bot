# -*- coding: utf-8 -*-
"""Saralash — admin tomoni.

Ikki qism:
  1) Vakansiyaga savol shablonini biriktirish (vq:*)
  2) Nomzod kartochkasi ustidagi harakatlar (cd:*) — video, test/yozma
     javoblarni ko'rish, baholash, tasdiqlash/rad etish.

Alohida "saralash paneli" YO'Q — HR barcha ishni nomzod xabari ostidagi
tugmalar orqali bajaradi, umumiy reyting esa Excel eksportda beriladi.
"""
import html
from datetime import datetime

from aiogram import Router, Bot
from aiogram.types import CallbackQuery

from app.database.crud import (
    get_vacancy, get_all_vacancies, get_application, get_application_answers,
    count_vacancy_questions, set_questions_from_bank, delete_vacancy_questions,
    update_answer_score, recompute_scores, update_application,
)
from app.keyboards.inline import (
    vacancy_questions_menu_keyboard, question_templates_keyboard,
    candidate_actions_keyboard, candidate_decided_keyboard,
    confirm_decision_keyboard, grade_menu_keyboard,
    grade_written_keyboard, grade_video_keyboard,
)
from app.question_bank import (
    color_for, MAX_TEST, MAX_WRITTEN, MAX_VIDEO, MAX_TOTAL,
    match_bank_key, QUESTION_BANK,
)
from app.handlers.admin import get_role, is_hr

router = Router()


def esc(v) -> str:
    return html.escape(str(v)) if v is not None else "—"


async def _guard(callback: CallbackQuery) -> bool:
    role = await get_role(callback.from_user.id)
    if not is_hr(role):
        await callback.answer("❌ Ruxsat yo'q.")
        return False
    return True


def _app_id(callback: CallbackQuery, pos: int = 2) -> int | None:
    try:
        return int(callback.data.split(":")[pos])
    except (ValueError, IndexError):
        return None


# ══════════════════════════════════════════════════════════════════════════
#  Vakansiya savollarini biriktirish
# ══════════════════════════════════════════════════════════════════════════

@router.callback_query(lambda c: c.data.startswith("vq:menu:"))
async def vq_menu(callback: CallbackQuery):
    if not await _guard(callback):
        return
    vid = _app_id(callback)
    v = await get_vacancy(vid) if vid else None
    if not v:
        await callback.answer("Vakansiya topilmadi.", show_alert=True)
        return
    n = await count_vacancy_questions(vid)
    text = (
        f"📝 <b>{esc(v.title)}</b> — saralash savollari\n\n"
        f"Biriktirilgan savollar: <b>{n} ta</b>\n\n"
        + ("Savollar bor — nomzodlar to'liq saralashdan (test + yozma + video) o'tadi.\n"
           if n else
           "Savol yo'q — bu vakansiyaga faqat oddiy ariza olinadi.\n")
        + "\nTayyor shablonni tanlang (3 test + 2 yozma + 1 video-savol)."
    )
    await callback.message.answer(text, parse_mode="HTML",
                                  reply_markup=vacancy_questions_menu_keyboard(vid, n > 0))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vq:tmpl:"))
async def vq_templates(callback: CallbackQuery):
    if not await _guard(callback):
        return
    vid = _app_id(callback)
    await callback.message.answer(
        "📋 <b>Shablonni tanlang</b>\n\n"
        "Tanlangan lavozim savollari shu vakansiyaga nusxalanadi. "
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
    try:
        vid, key = int(parts[2]), parts[3]
    except (ValueError, IndexError):
        await callback.answer("Xato.")
        return
    n = await set_questions_from_bank(vid, key)
    if n == 0:
        await callback.answer("Shablon topilmadi.", show_alert=True)
        return
    v = await get_vacancy(vid)
    await callback.message.answer(
        f"✅ <b>{esc(v.title)}</b> vakansiyasiga {n} ta savol biriktirildi.\n\n"
        f"Endi nomzodlar to'liq saralashdan o'tadi:\n"
        f"3 ta test → 2 ta yozma → 1 ta majburiy video.",
        parse_mode="HTML",
        reply_markup=vacancy_questions_menu_keyboard(vid, True)
    )
    await callback.answer("Biriktirildi ✅")


@router.callback_query(lambda c: c.data == "vq:autoall")
async def vq_auto_all(callback: CallbackQuery):
    if not await _guard(callback):
        return
    await callback.answer("Biriktirilmoqda…")
    vacancies = await get_all_vacancies()
    attached, skipped, unmatched = [], [], []
    for v in vacancies:
        if await count_vacancy_questions(v.id) > 0:
            skipped.append(v.title)
            continue
        key = match_bank_key(v.title)
        if not key:
            unmatched.append(v.title)
            continue
        await set_questions_from_bank(v.id, key)
        attached.append(f"{v.title} → {QUESTION_BANK[key]['title']}")

    lines = ["🤖 <b>Avtomatik biriktirish natijasi</b>\n"]
    if attached:
        lines.append("✅ <b>Biriktirildi:</b>")
        lines += [f"• {esc(x)}" for x in attached]
        lines.append("")
    if skipped:
        lines.append("⏭ <b>Savoli bor (o'tkazildi):</b>")
        lines += [f"• {esc(x)}" for x in skipped]
        lines.append("")
    if unmatched:
        lines.append("⚠️ <b>Mos topilmadi (qo'lda biriktiring):</b>")
        lines += [f"• {esc(x)}" for x in unmatched]
        lines.append("\n<i>Vakansiya → 📝 Savollar → 📋 Shablondan yuklash.</i>")
    if not vacancies:
        lines.append("Vakansiya yo'q.")
    await callback.message.answer("\n".join(lines), parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith("vq:clear:"))
async def vq_clear(callback: CallbackQuery):
    if not await _guard(callback):
        return
    vid = _app_id(callback)
    await delete_vacancy_questions(vid)
    await callback.message.answer(
        "🗑 Savollar o'chirildi. Endi bu vakansiyaga faqat oddiy ariza olinadi.",
        reply_markup=vacancy_questions_menu_keyboard(vid, False)
    )
    await callback.answer("O'chirildi")


# ══════════════════════════════════════════════════════════════════════════
#  Nomzod kartochkasi — harakatlar (xabar ostidagi tugmalar)
# ══════════════════════════════════════════════════════════════════════════

STATUS_LABEL = {
    "submitted":   "🕐 Ko'rib chiqilmoqda",
    "approved":    "✅ Tasdiqlangan",
    "rejected":    "❌ Rad etilgan",
    "in_progress": "⏳ Tugatilmagan",
}


def _fmt(v, mx):
    return f"{v}/{mx}" if v is not None else f"—/{mx}"


async def _summary(app) -> str:
    """Ball xulosasi — kartochka ostiga qo'shiladi."""
    color = color_for(app.total_score) if app.total_score is not None else "⚪️"
    return (
        f"{color} <b>{STATUS_LABEL.get(app.status, app.status)}</b>\n"
        f"🧠 Test: {_fmt(app.test_score, MAX_TEST)} · "
        f"✍️ Yozma: {_fmt(app.written_score, MAX_WRITTEN)} · "
        f"🎬 Video: {_fmt(app.video_score, MAX_VIDEO)}\n"
        f"⭐️ <b>Jami: {_fmt(app.total_score, MAX_TOTAL)}</b>"
    )


async def _refresh_markup(callback: CallbackQuery, app):
    """Xabar ostidagi tugmalarni holatga qarab yangilaydi."""
    kb = (candidate_actions_keyboard(app) if app.status == "submitted"
          else candidate_decided_keyboard(app))
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass


@router.callback_query(lambda c: c.data.startswith("cd:video:"))
async def cd_video(callback: CallbackQuery, bot: Bot):
    if not await _guard(callback):
        return
    app = await get_application(_app_id(callback))
    if not app or not app.video_file_id:
        await callback.answer("Video yo'q.", show_alert=True)
        return
    try:
        cap = f"🎥 Ariza #{app.id} — {esc(app.full_name)}"
        if app.video_is_note:
            await bot.send_video_note(callback.from_user.id, app.video_file_id)
            await bot.send_message(callback.from_user.id, cap, parse_mode="HTML")
        else:
            await bot.send_video(callback.from_user.id, app.video_file_id,
                                 caption=cap, parse_mode="HTML")
        await callback.answer("Video yuborildi ✅")
    except Exception as e:
        await callback.answer(f"Yuborilmadi: {e}", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("cd:tests:"))
async def cd_tests(callback: CallbackQuery, bot: Bot):
    if not await _guard(callback):
        return
    app_id = _app_id(callback)
    app = await get_application(app_id)
    answers = await get_application_answers(app_id)
    tests = [a for a in answers if a.qtype == "test"]
    if not tests:
        await callback.answer("Test javoblari yo'q.", show_alert=True)
        return
    lines = [f"🧠 <b>Test javoblari</b> — ariza #{app_id}",
             f"👤 {esc(app.full_name)}\n"]
    for i, a in enumerate(tests, start=1):
        mark = "✅" if (a.score or 0) == 3 else ("🟡" if (a.score or 0) == 1 else "❌")
        lines.append(f"<b>{i}.</b> {esc(a.question_text)}")
        lines.append(f"{mark} <i>{esc(a.answer_text)}</i> — <b>{a.score or 0}/3</b>\n")
    lines.append(f"<b>Jami: {app.test_score if app.test_score is not None else 0}/{MAX_TEST}</b>")
    await _send_long(bot, callback.from_user.id, "\n".join(lines))
    await callback.answer("Yuborildi ✅")


@router.callback_query(lambda c: c.data.startswith("cd:written:"))
async def cd_written(callback: CallbackQuery, bot: Bot):
    if not await _guard(callback):
        return
    app_id = _app_id(callback)
    app = await get_application(app_id)
    answers = await get_application_answers(app_id)
    written = [a for a in answers if a.qtype == "written"]
    if not written:
        await callback.answer("Yozma javoblar yo'q.", show_alert=True)
        return
    lines = [f"✍️ <b>Yozma javoblar</b> — ariza #{app_id}",
             f"👤 {esc(app.full_name)}\n"]
    for i, a in enumerate(written, start=1):
        sc = f"{a.score}/3" if a.score is not None else "⚠️ baholanmagan"
        lines.append(f"<b>{i}.</b> {esc(a.question_text)}")
        lines.append(f"<i>{esc(a.answer_text)}</i>")
        lines.append(f"➡️ {sc}\n")
    await _send_long(bot, callback.from_user.id, "\n".join(lines))
    await callback.answer("Yuborildi ✅")


async def _send_long(bot: Bot, chat_id: int, text: str, limit: int = 3800):
    """Uzun matnni bo'lib yuboradi (Telegram 4096 belgi chegarasi)."""
    while text:
        chunk, text = text[:limit], text[limit:]
        if text:
            cut_at = chunk.rfind("\n")
            if cut_at > limit // 2:
                text, chunk = chunk[cut_at:] + text, chunk[:cut_at]
        try:
            await bot.send_message(chat_id, chunk, parse_mode="HTML")
        except Exception:
            await bot.send_message(chat_id, html.escape(chunk))


# ── Baholash ───────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data.startswith("cd:grade:"))
async def cd_grade_menu(callback: CallbackQuery):
    if not await _guard(callback):
        return
    app_id = _app_id(callback)
    app = await get_application(app_id)
    if not app:
        await callback.answer("Nomzod topilmadi.", show_alert=True)
        return
    answers = await get_application_answers(app_id)
    written = [a for a in answers if a.qtype == "written"]
    try:
        await callback.message.edit_reply_markup(
            reply_markup=grade_menu_keyboard(app, written))
    except Exception:
        pass
    await callback.answer("Baholash: yozma va video")


@router.callback_query(lambda c: c.data.startswith("cd:back:"))
async def cd_back(callback: CallbackQuery):
    if not await _guard(callback):
        return
    app = await get_application(_app_id(callback))
    if app:
        await _refresh_markup(callback, app)
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("cd:wgrade:"))
async def cd_written_grade(callback: CallbackQuery, bot: Bot):
    if not await _guard(callback):
        return
    parts = callback.data.split(":")
    try:
        app_id, answer_id = int(parts[2]), int(parts[3])
    except (ValueError, IndexError):
        await callback.answer("Xato.")
        return
    answers = await get_application_answers(app_id)
    ans = next((a for a in answers if a.id == answer_id), None)
    if not ans:
        await callback.answer("Javob topilmadi.", show_alert=True)
        return
    await _send_long(bot, callback.from_user.id,
                     f"✍️ <b>Baholanayotgan javob</b>\n\n"
                     f"<b>Savol:</b> {esc(ans.question_text)}\n\n"
                     f"<b>Javob:</b>\n<i>{esc(ans.answer_text)}</i>\n\n"
                     f"Mezon: mavzuga aloqadorlik, mantiq, aniqlik, savodxonlik.")
    try:
        await callback.message.edit_reply_markup(
            reply_markup=grade_written_keyboard(app_id, answer_id))
    except Exception:
        pass
    await callback.answer("Javob yuborildi — ball tanlang (0-3)")


@router.callback_query(lambda c: c.data.startswith("cd:wset:"))
async def cd_written_set(callback: CallbackQuery):
    if not await _guard(callback):
        return
    parts = callback.data.split(":")
    try:
        app_id, answer_id, score = int(parts[2]), int(parts[3]), int(parts[4])
    except (ValueError, IndexError):
        await callback.answer("Xato.")
        return
    await update_answer_score(answer_id, score)
    app = await recompute_scores(app_id)
    answers = await get_application_answers(app_id)
    written = [a for a in answers if a.qtype == "written"]
    try:
        await callback.message.edit_reply_markup(
            reply_markup=grade_menu_keyboard(app, written))
    except Exception:
        pass
    await callback.answer(f"✅ Yozma: {score}/3")


@router.callback_query(lambda c: c.data.startswith("cd:vgrade:"))
async def cd_video_grade(callback: CallbackQuery):
    if not await _guard(callback):
        return
    app_id = _app_id(callback)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=grade_video_keyboard(app_id))
    except Exception:
        pass
    await callback.answer("Videoga ball bering (0-4): nutq/ishonch + mazmun")


@router.callback_query(lambda c: c.data.startswith("cd:vset:"))
async def cd_video_set(callback: CallbackQuery):
    if not await _guard(callback):
        return
    parts = callback.data.split(":")
    try:
        app_id, score = int(parts[2]), int(parts[3])
    except (ValueError, IndexError):
        await callback.answer("Xato.")
        return
    await update_application(app_id, video_score=score)
    app = await recompute_scores(app_id)
    answers = await get_application_answers(app_id)
    written = [a for a in answers if a.qtype == "written"]
    try:
        await callback.message.edit_reply_markup(
            reply_markup=grade_menu_keyboard(app, written))
    except Exception:
        pass
    total = f" · Jami: {app.total_score}/{MAX_TOTAL}" if app and app.total_score is not None else ""
    await callback.answer(f"✅ Video: {score}/4{total}")


# ── Tasdiqlash / Rad etish (tasdiq bilan) ─────────────────────────────────

@router.callback_query(lambda c: c.data.startswith("cd:ask_ok:"))
async def cd_ask_ok(callback: CallbackQuery):
    if not await _guard(callback):
        return
    app_id = _app_id(callback)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=confirm_decision_keyboard(app_id, "ok"))
    except Exception:
        pass
    await callback.answer("Nomzodga taklif xabari yuboriladi. Tasdiqlaysizmi?", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("cd:ask_no:"))
async def cd_ask_no(callback: CallbackQuery):
    if not await _guard(callback):
        return
    app_id = _app_id(callback)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=confirm_decision_keyboard(app_id, "no"))
    except Exception:
        pass
    await callback.answer("Nomzodga RAD xabari yuboriladi. Tasdiqlaysizmi?", show_alert=True)


async def _decide(callback: CallbackQuery, bot: Bot, app_id: int, approve: bool):
    app = await get_application(app_id)
    if not app:
        await callback.answer("Nomzod topilmadi.", show_alert=True)
        return
    status = "approved" if approve else "rejected"
    # DIQQAT: ariza O'CHIRILMAYDI — faqat holati o'zgaradi, ma'lumot bazada qoladi
    await update_application(app_id, status=status,
                             reviewed_by=callback.from_user.id,
                             reviewed_at=datetime.now())
    msg = (
        "🎉 <b>Tabriklaymiz!</b> Siz suhbatga taklif qilindingiz.\n"
        "HR mutaxassisimiz qulay vaqtni kelishish uchun siz bilan bog'lanadi."
        if approve else
        "Ariza uchun rahmat. Afsuski, bu vakansiya bo'yicha boshqa nomzodni tanladik.\n"
        "Ma'lumotlaringiz bazamizda saqlanadi va mos vakansiya chiqsa, siz bilan bog'lanamiz."
    )
    try:
        await bot.send_message(app.user_id, msg, parse_mode="HTML")
        note = "✅ Nomzodga xabar yuborildi."
    except Exception:
        note = "⚠️ Nomzodga xabar yetmadi (botni bloklagan bo'lishi mumkin)."

    app = await get_application(app_id)
    await _refresh_markup(callback, app)
    label = "TASDIQLANDI" if approve else "RAD ETILDI"
    await callback.answer(f"{label}. {note}", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("cd:do_ok:"))
async def cd_do_ok(callback: CallbackQuery, bot: Bot):
    if not await _guard(callback):
        return
    await _decide(callback, bot, _app_id(callback), approve=True)


@router.callback_query(lambda c: c.data.startswith("cd:do_no:"))
async def cd_do_no(callback: CallbackQuery, bot: Bot):
    if not await _guard(callback):
        return
    await _decide(callback, bot, _app_id(callback), approve=False)


@router.callback_query(lambda c: c.data.startswith("cd:undo:"))
async def cd_undo(callback: CallbackQuery):
    if not await _guard(callback):
        return
    app_id = _app_id(callback)
    await update_application(app_id, status="submitted", reviewed_by=None, reviewed_at=None)
    app = await get_application(app_id)
    await _refresh_markup(callback, app)
    await callback.answer("↩️ Qaror qaytarildi (nomzodga xabar ketmaydi).", show_alert=True)
