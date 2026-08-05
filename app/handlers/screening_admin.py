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
import json
from datetime import datetime

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.database.crud import (
    get_vacancy, get_all_vacancies, get_application, get_application_answers,
    count_vacancy_questions, set_questions_from_bank, delete_vacancy_questions,
    update_answer_score, recompute_scores, update_application,
    get_vacancy_questions, save_question_set, get_question, update_question_text,
    update_question_option, delete_question, add_question, update_vacancy,
)
from app.keyboards.inline import (
    vacancy_questions_menu_keyboard, question_templates_keyboard,
    candidate_actions_keyboard, candidate_decided_keyboard,
    confirm_decision_keyboard, grade_menu_keyboard,
    grade_written_keyboard, grade_video_keyboard,
    ai_questions_review_keyboard, questions_list_keyboard, question_detail_keyboard,
    stage_settings_keyboard, mode_choice_keyboard, MODE_LABEL,
)
from app.states.admin_state import QuestionEditState
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


def _ai_on() -> bool:
    """AI baholash yoqilganmi (ANTHROPIC_API_KEY bor va paket o'rnatilgan)."""
    try:
        from app.ai_grader import is_enabled
        return is_enabled()
    except Exception:
        return False


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
        + "\n<b>To'liq to'plam:</b> 3 test + 2 yozma + 1 majburiy video-savol.\n\n"
        + ("🤖 <b>AI bilan yaratish</b> — shu lavozimga moslab yangi savollar tuzadi "
           "(har qanday lavozim uchun).\n" if _aiq_on() else "")
        + "📋 <b>Shablondan</b> — 22 ta tayyor lavozimdan biri.\n"
        + "✏️ <b>Tahrirlash</b> — savollarni qo'lda yozish yoki o'zgartirish."
    )
    await callback.message.answer(text, parse_mode="HTML",
                                  reply_markup=vacancy_questions_menu_keyboard(vid, n > 0, _aiq_on()))
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
        reply_markup=vacancy_questions_menu_keyboard(vid, True, _aiq_on())
    )
    await callback.answer("Biriktirildi ✅")


@router.callback_query(lambda c: c.data in ("vq:autoall", "vq:autoall:force"))
async def vq_auto_all(callback: CallbackQuery):
    """Barcha vakansiyaga nomiga qarab savol biriktiradi.

    vq:autoall        — faqat savoli YO'Q vakansiyalarga
    vq:autoall:force  — HAMMASINI eng yangi shablon bilan qayta yozadi
    """
    if not await _guard(callback):
        return
    force = callback.data.endswith(":force")
    await callback.answer("Biriktirilmoqda…")
    vacancies = await get_all_vacancies()
    attached, skipped, unmatched = [], [], []
    for v in vacancies:
        has_q = await count_vacancy_questions(v.id) > 0
        if has_q and not force:
            skipped.append(v.title)
            continue
        key = match_bank_key(v.title)
        if not key:
            unmatched.append(v.title)
            continue
        await set_questions_from_bank(v.id, key)
        attached.append(f"{v.title} → {QUESTION_BANK[key]['title']}")

    head = ("🔄 <b>Savollar yangilandi</b>" if force else "🤖 <b>Avtomatik biriktirish</b>")
    lines = [head + "\n"]
    if attached:
        lines.append(f"✅ <b>{len(attached)} ta vakansiya</b> "
                     f"(3 test + 2 yozma + 1 video):")
        lines += [f"• {esc(x)}" for x in attached]
        lines.append("")
    if skipped:
        lines.append(f"⏭ <b>Savoli bor — o'tkazildi ({len(skipped)}):</b>")
        lines += [f"• {esc(x)}" for x in skipped]
        lines.append("<i>Yangilash uchun «🔄 Savollarni yangilash» tugmasidan foydalaning.</i>\n")
    if unmatched:
        lines.append(f"⚠️ <b>Mos topilmadi ({len(unmatched)}) — qo'lda biriktiring:</b>")
        lines += [f"• {esc(x)}" for x in unmatched]
        lines.append("\n<i>Vakansiya → 📝 Savollar → 📋 Shablondan yuklash.</i>")
    if not vacancies:
        lines.append("Vakansiya yo'q.")
    await _send_long(callback.bot, callback.from_user.id, "\n".join(lines))


@router.callback_query(lambda c: c.data.startswith("vq:clear:"))
async def vq_clear(callback: CallbackQuery):
    if not await _guard(callback):
        return
    vid = _app_id(callback)
    await delete_vacancy_questions(vid)
    await callback.message.answer(
        "🗑 Savollar o'chirildi. Endi bu vakansiyaga faqat oddiy ariza olinadi.",
        reply_markup=vacancy_questions_menu_keyboard(vid, False, _aiq_on())
    )
    await callback.answer("O'chirildi")


# ══════════════════════════════════════════════════════════════════════════
#  Saralash bosqichlarini boshqarish (yoqish / o'chirish / ixtiyoriy)
# ══════════════════════════════════════════════════════════════════════════

async def _stage_settings_text(v) -> str:
    from app.question_bank import stage_max, STAGE_ON, MAX_TEST, MAX_WRITTEN, MAX_VIDEO
    q_mode = getattr(v, "questions_mode", "required") or "required"
    v_mode = getattr(v, "video_mode", "required") or "required"
    n = await count_vacancy_questions(v.id)

    lines = [f"⚙️ <b>{esc(v.title)}</b> — saralash bosqichlari\n"]
    lines.append("<b>1️⃣ Ma'lumotlar</b> — doim so'raladi (ism, tel, yosh, maosh…)")

    qm = {"required": f"🔴 majburiy — javob bermay ariza yakunlanmaydi",
          "optional": "🟡 ixtiyoriy — nomzod o'tkazib yuborishi mumkin (0 ball)",
          "off": "⚫️ o'chirilgan — test va yozma umuman so'ralmaydi"}
    lines.append(f"<b>2️⃣ Savollar</b> — {qm.get(q_mode, q_mode)}")
    if q_mode in STAGE_ON:
        if n:
            lines.append(f"   <i>{n} ta savol biriktirilgan</i>")
        else:
            lines.append("   ⚠️ <b>Savol biriktirilmagan!</b> "
                         "<i>📝 Savollar bo'limidan qo'shing, aks holda bosqich "
                         "o'tkazib yuboriladi va nomzod 0 ball oladi.</i>")

    vm = {"required": "🔴 majburiy — videosiz ariza qabul qilinmaydi",
          "optional": "🟡 ixtiyoriy — nomzod o'tkazib yuborishi mumkin (0 ball)",
          "off": "⚫️ o'chirilgan — video umuman so'ralmaydi"}
    lines.append(f"<b>3️⃣ Video</b> — {vm.get(v_mode, v_mode)}")

    mx = stage_max(q_mode, v_mode)
    detail = []
    if q_mode in STAGE_ON:
        detail.append(f"test {MAX_TEST} + yozma {MAX_WRITTEN}")
    if v_mode in STAGE_ON:
        detail.append(f"video {MAX_VIDEO}")
    lines.append(f"\n📊 <b>Maksimal ball: {mx}</b> "
                 f"({' + '.join(detail) if detail else 'baholanmaydi'})")

    if mx == 0:
        lines.append("\n⚠️ <b>Barcha bosqich o'chirilgan</b> — bu vakansiyaga faqat "
                     "oddiy ariza olinadi, ball qo'yilmaydi.")
    elif "optional" in (q_mode, v_mode):
        lines.append("<i>Ixtiyoriy bosqich ham maksimalga kiradi — "
                     "o'tkazib yuborgan nomzod 0 ball oladi.</i>")

    lines.append("\n<i>O'zgartirish faqat YANGI arizalarga ta'sir qiladi.</i>")
    return "\n".join(lines)


@router.callback_query(lambda c: c.data.startswith("vs:menu:"))
async def vs_menu(callback: CallbackQuery):
    if not await _guard(callback):
        return
    v = await get_vacancy(_app_id(callback))
    if not v:
        await callback.answer("Vakansiya topilmadi.", show_alert=True)
        return
    await callback.message.answer(await _stage_settings_text(v), parse_mode="HTML",
                                  reply_markup=stage_settings_keyboard(v))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vs:qmenu:"))
async def vs_questions_menu(callback: CallbackQuery):
    if not await _guard(callback):
        return
    v = await get_vacancy(_app_id(callback))
    if not v:
        await callback.answer("Vakansiya topilmadi.", show_alert=True)
        return
    await callback.message.answer(
        "🧠 <b>Savollar bosqichi</b> (3 test + 2 yozma)\n\n"
        "🔴 <b>Majburiy</b> — nomzod barcha savolga javob bermasa ariza "
        "yakunlanmaydi.\n\n"
        "🟡 <b>Ixtiyoriy</b> — bosqich boshida «▶️ Boshlash» va "
        "«⏭ O'tkazib yuborish» tugmalari chiqadi. O'tkazib yuborgan nomzod "
        "test va yozma uchun <b>0 ball</b> oladi, lekin arizasi qabul qilinadi.\n\n"
        "⚫️ <b>O'chirilgan</b> — savollar umuman so'ralmaydi, maksimal ball "
        "15 ballga kamayadi.",
        parse_mode="HTML",
        reply_markup=mode_choice_keyboard(v.id, v.questions_mode or "required", "q"))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vs:vmenu:"))
async def vs_video_menu(callback: CallbackQuery):
    if not await _guard(callback):
        return
    v = await get_vacancy(_app_id(callback))
    if not v:
        await callback.answer("Vakansiya topilmadi.", show_alert=True)
        return
    await callback.message.answer(
        "🎥 <b>Video bosqichi</b>\n\n"
        "🔴 <b>Majburiy</b> — nomzod video yubormasa ariza yakunlanmaydi va "
        "HRga yuborilmaydi.\n\n"
        "🟡 <b>Ixtiyoriy</b> — video so'raladi, lekin «⏭ O'tkazib yuborish» "
        "tugmasi chiqadi. O'tkazib yuborgan nomzod video uchun <b>0 ball</b> "
        "oladi, lekin arizasi qabul qilinadi.\n\n"
        "⚫️ <b>O'chirilgan</b> — video umuman so'ralmaydi, maksimal ball "
        "4 ballga kamayadi.",
        parse_mode="HTML",
        reply_markup=mode_choice_keyboard(v.id, v.video_mode or "required", "v"))
    await callback.answer()


async def _set_mode(callback: CallbackQuery, field: str, icon: str):
    parts = callback.data.split(":")
    try:
        vid, mode = int(parts[2]), parts[3]
    except (ValueError, IndexError):
        await callback.answer("Xato.")
        return
    if mode not in ("required", "optional", "off"):
        await callback.answer("Noma'lum rejim.", show_alert=True)
        return
    await update_vacancy(vid, **{field: mode})
    v = await get_vacancy(vid)
    text = await _stage_settings_text(v)
    try:
        await callback.message.edit_text(text, parse_mode="HTML",
                                         reply_markup=stage_settings_keyboard(v))
    except Exception:
        await callback.message.answer(text, parse_mode="HTML",
                                      reply_markup=stage_settings_keyboard(v))
    await callback.answer(f"{icon} {MODE_LABEL.get(mode, mode)}")


@router.callback_query(lambda c: c.data.startswith("vs:qset:"))
async def vs_questions_set(callback: CallbackQuery):
    if not await _guard(callback):
        return
    await _set_mode(callback, "questions_mode", "🧠 Savollar:")


@router.callback_query(lambda c: c.data.startswith("vs:vset:"))
async def vs_video_set(callback: CallbackQuery):
    if not await _guard(callback):
        return
    await _set_mode(callback, "video_mode", "🎥 Video:")


# ══════════════════════════════════════════════════════════════════════════
#  AI bilan savol yaratish
# ══════════════════════════════════════════════════════════════════════════

def _aiq_on() -> bool:
    try:
        from app.ai_questions import is_enabled
        return is_enabled()
    except Exception:
        return False


@router.callback_query(lambda c: c.data.startswith("vq:ai:"))
async def vq_ai_generate(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not await _guard(callback):
        return
    vid = _app_id(callback)
    v = await get_vacancy(vid)
    if not v:
        await callback.answer("Vakansiya topilmadi.", show_alert=True)
        return
    from app.ai_questions import is_enabled, generate_questions, preview_text
    if not is_enabled():
        await callback.answer(
            "AI yoqilmagan. .env ga ANTHROPIC_API_KEY qo'shib, botni restart qiling.",
            show_alert=True)
        return

    await callback.answer("🤖 Yaratilmoqda… (15-30 soniya)")
    msg = await callback.message.answer(
        f"🤖 <b>{esc(v.title)}</b> uchun savollar yaratilmoqda…\n"
        f"<i>Bu 15-30 soniya vaqt oladi.</i>", parse_mode="HTML")

    data = await generate_questions(v.title, v.requirements)
    try:
        await msg.delete()
    except Exception:
        pass

    if not data:
        await callback.message.answer(
            "⚠️ Savol yaratib bo'lmadi (tarmoq yoki kalit muammosi).\n"
            "Qayta urinib ko'ring yoki tayyor shablondan yuklang.",
            reply_markup=vacancy_questions_menu_keyboard(vid, False, True))
        return

    await state.set_state(QuestionEditState.review)
    await state.update_data(gen=data, gen_vid=vid)
    await _send_long(bot, callback.from_user.id, preview_text(data))
    await callback.message.answer(
        "👆 Yuqoridagi savollarni ko'rib chiqing.\n\n"
        "<i>Saqlagandan keyin har bir savolni alohida tahrirlashingiz mumkin.</i>",
        parse_mode="HTML",
        reply_markup=ai_questions_review_keyboard(vid))


@router.callback_query(QuestionEditState.review, lambda c: c.data.startswith("vq:aisave:"))
async def vq_ai_save(callback: CallbackQuery, state: FSMContext):
    if not await _guard(callback):
        return
    vid = _app_id(callback)
    data = await state.get_data()
    gen = data.get("gen")
    if not gen or data.get("gen_vid") != vid:
        await callback.answer("Ma'lumot yo'qoldi, qayta yarating.", show_alert=True)
        return
    n = await save_question_set(vid, gen)
    await state.clear()
    v = await get_vacancy(vid)
    await callback.message.answer(
        f"✅ <b>{esc(v.title)}</b> vakansiyasiga {n} ta savol saqlandi.\n\n"
        f"Endi nomzodlar to'liq saralashdan o'tadi:\n"
        f"3 ta test → 2 ta yozma → 1 ta majburiy video.",
        parse_mode="HTML",
        reply_markup=vacancy_questions_menu_keyboard(vid, True, _aiq_on()))
    await callback.answer("Saqlandi ✅")


# ══════════════════════════════════════════════════════════════════════════
#  Savollarni qo'lda tahrirlash
# ══════════════════════════════════════════════════════════════════════════

async def _questions_list(callback: CallbackQuery, vid: int, note: str = ""):
    v = await get_vacancy(vid)
    qs = await get_vacancy_questions(vid)
    counts = {}
    for q in qs:
        counts[q.qtype] = counts.get(q.qtype, 0) + 1
    head = (
        f"✏️ <b>{esc(v.title if v else vid)}</b> — savollar\n\n"
        f"🧠 Test: {counts.get('test', 0)} ta · "
        f"✍️ Yozma: {counts.get('written', 0)} ta · "
        f"🎥 Video: {counts.get('video', 0)} ta\n\n"
        f"<i>To'liq to'plam: 3 test + 2 yozma + 1 video.\n"
        f"Tahrirlash uchun savolni tanlang.</i>"
    )
    if note:
        head = note + "\n\n" + head
    await callback.message.answer(head, parse_mode="HTML",
                                  reply_markup=questions_list_keyboard(vid, qs))


@router.callback_query(lambda c: c.data.startswith("vq:edit:"))
async def vq_edit_list(callback: CallbackQuery, state: FSMContext):
    if not await _guard(callback):
        return
    await state.clear()
    await _questions_list(callback, _app_id(callback))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vq:q:"))
async def vq_question_detail(callback: CallbackQuery, state: FSMContext):
    if not await _guard(callback):
        return
    await state.clear()
    qid = _app_id(callback)
    q = await get_question(qid)
    if not q:
        await callback.answer("Savol topilmadi.", show_alert=True)
        return

    letters = ["A", "B", "C", "D", "E"]
    kind = {"test": "🧠 Test savoli", "written": "✍️ Yozma savol",
            "video": "🎥 Video-savol"}.get(q.qtype, q.qtype)
    lines = [f"{kind} #{q.order_num}\n", f"<b>{esc(q.text)}</b>"]
    n_opt = 0
    if q.qtype == "test" and q.options:
        opts = json.loads(q.options)
        n_opt = len(opts)
        lines.append("")
        for i, o in enumerate(opts):
            lines.append(f"<b>{letters[i]})</b> {esc(o['text'])} — <i>{o['score']} ball</i>")
        lines.append("\n<i>Ballar o'zgarmaydi — faqat matnni tahrirlash mumkin.</i>")
    elif q.qtype == "written":
        lines.append(f"\n<i>Baholash: 0-3 ball (HR yoki AI)</i>")
    else:
        lines.append(f"\n<i>Baholash: 0-4 ball. Bot oldiga «o'zingizni tanishtiring» "
                     f"qismini avtomatik qo'shadi.</i>")

    await callback.message.answer("\n".join(lines), parse_mode="HTML",
                                  reply_markup=question_detail_keyboard(q, n_opt))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("vq:qtext:"))
async def vq_edit_text_start(callback: CallbackQuery, state: FSMContext):
    if not await _guard(callback):
        return
    qid = _app_id(callback)
    q = await get_question(qid)
    if not q:
        await callback.answer("Savol topilmadi.", show_alert=True)
        return
    await state.set_state(QuestionEditState.q_text)
    await state.update_data(qid=qid)
    await callback.message.answer(
        f"✏️ <b>Savol matnini yozing</b>\n\n"
        f"Hozirgi matn:\n<i>{esc(q.text)}</i>\n\n"
        f"Yangi matnni yuboring:",
        parse_mode="HTML")
    await callback.answer()


@router.message(QuestionEditState.q_text, F.text)
async def vq_edit_text_save(message: Message, state: FSMContext):
    data = await state.get_data()
    q = await update_question_text(data["qid"], message.text.strip())
    await state.clear()
    if not q:
        await message.answer("⚠️ Savol topilmadi.")
        return
    qs = await get_vacancy_questions(q.vacancy_id)
    await message.answer(
        "✅ Savol matni yangilandi.", parse_mode="HTML",
        reply_markup=questions_list_keyboard(q.vacancy_id, qs))


@router.callback_query(lambda c: c.data.startswith("vq:opt:"))
async def vq_edit_option_start(callback: CallbackQuery, state: FSMContext):
    if not await _guard(callback):
        return
    parts = callback.data.split(":")
    try:
        qid, pos = int(parts[2]), int(parts[3])
    except (ValueError, IndexError):
        await callback.answer("Xato.")
        return
    q = await get_question(qid)
    if not q or not q.options:
        await callback.answer("Savol topilmadi.", show_alert=True)
        return
    opts = json.loads(q.options)
    if not (0 <= pos < len(opts)):
        await callback.answer("Variant topilmadi.", show_alert=True)
        return
    letters = ["A", "B", "C", "D", "E"]
    await state.set_state(QuestionEditState.opt_text)
    await state.update_data(qid=qid, pos=pos)
    await callback.message.answer(
        f"✏️ <b>{letters[pos]}) variant matnini yozing</b>\n"
        f"<i>Bu variant {opts[pos]['score']} ball beradi — ball o'zgarmaydi.</i>\n\n"
        f"Hozirgi matn:\n<i>{esc(opts[pos]['text'])}</i>\n\n"
        f"Yangi matnni yuboring:",
        parse_mode="HTML")
    await callback.answer()


@router.message(QuestionEditState.opt_text, F.text)
async def vq_edit_option_save(message: Message, state: FSMContext):
    data = await state.get_data()
    q = await update_question_option(data["qid"], data["pos"], message.text.strip())
    await state.clear()
    if not q:
        await message.answer("⚠️ Variant yangilanmadi.")
        return
    qs = await get_vacancy_questions(q.vacancy_id)
    await message.answer(
        "✅ Variant matni yangilandi.", parse_mode="HTML",
        reply_markup=questions_list_keyboard(q.vacancy_id, qs))


@router.callback_query(lambda c: c.data.startswith("vq:qdel:"))
async def vq_delete_question(callback: CallbackQuery):
    if not await _guard(callback):
        return
    qid = _app_id(callback)
    q = await get_question(qid)
    if not q:
        await callback.answer("Savol topilmadi.", show_alert=True)
        return
    vid = q.vacancy_id
    await delete_question(qid)
    await _questions_list(callback, vid, "🗑 Savol o'chirildi.")
    await callback.answer("O'chirildi")


# ── Yangi savol qo'shish ───────────────────────────────────────────────────

@router.callback_query(lambda c: c.data.startswith("vq:add:"))
async def vq_add_start(callback: CallbackQuery, state: FSMContext):
    if not await _guard(callback):
        return
    parts = callback.data.split(":")
    try:
        qtype, vid = parts[2], int(parts[3])
    except (ValueError, IndexError):
        await callback.answer("Xato.")
        return
    await state.update_data(add_vid=vid)

    if qtype == "test":
        await state.set_state(QuestionEditState.new_test_q)
        await callback.message.answer(
            "🧠 <b>Yangi test savoli</b>\n\n"
            "Savol matnini yuboring.\n"
            "<i>Maslahat: real ish vaziyati bo'lsin, ta'rif so'ramasin.\n"
            "Masalan: «Obyektga zudlik bilan material kerak, lekin bazada yo'q. "
            "Nima qilasiz?»</i>",
            parse_mode="HTML")
    elif qtype == "written":
        await state.set_state(QuestionEditState.new_written)
        await callback.message.answer(
            "✍️ <b>Yangi yozma savol</b>\n\n"
            "Savol matnini yuboring.\n"
            "<i>Nomzod matn bilan javob beradi, HR yoki AI 0-3 ball qo'yadi.</i>",
            parse_mode="HTML")
    else:
        await state.set_state(QuestionEditState.new_video)
        await callback.message.answer(
            "🎥 <b>Video-savol</b>\n\n"
            "Savol matnini yuboring.\n"
            "<i>«Avval o'zingizni tanishtiring» qismini yozmang — bot uni "
            "o'zi qo'shadi. Faqat savolning o'zini yozing.\n"
            "Agar video-savol allaqachon bo'lsa, yangisi qo'shiladi — "
            "eskisini o'chirib qo'ying.</i>",
            parse_mode="HTML")
    await callback.answer()


@router.message(QuestionEditState.new_test_q, F.text)
async def vq_new_test_q(message: Message, state: FSMContext):
    await state.update_data(nq_text=message.text.strip())
    await state.set_state(QuestionEditState.new_test_o3)
    await message.answer(
        "✅ Savol qabul qilindi.\n\n"
        "Endi <b>eng to'g'ri javob</b>ni yuboring (3 ball).\n"
        "<i>Kasbiy jihatdan to'g'ri, tizimli yondashuv.</i>",
        parse_mode="HTML")


@router.message(QuestionEditState.new_test_o3, F.text)
async def vq_new_test_o3(message: Message, state: FSMContext):
    await state.update_data(nq_o3=message.text.strip())
    await state.set_state(QuestionEditState.new_test_o1)
    await message.answer(
        "Endi <b>qisman to'g'ri javob</b>ni yuboring (1 ball).\n"
        "<i>Amalda ko'p uchraydigan tezkor yo'l — natija beradi, lekin "
        "sababni yechmaydi. Uzunligi 3 ballik javobga yaqin bo'lsin.</i>",
        parse_mode="HTML")


@router.message(QuestionEditState.new_test_o1, F.text)
async def vq_new_test_o1(message: Message, state: FSMContext):
    await state.update_data(nq_o1=message.text.strip())
    await state.set_state(QuestionEditState.new_test_o0)
    await message.answer(
        "Endi <b>yaroqsiz javob</b>ni yuboring (0 ball).\n"
        "<i>Mas'uliyatdan qochish yoki qoidani buzish.</i>",
        parse_mode="HTML")


@router.message(QuestionEditState.new_test_o0, F.text)
async def vq_new_test_o0(message: Message, state: FSMContext):
    data = await state.get_data()
    vid = data["add_vid"]
    opts = [
        {"text": data["nq_o3"], "score": 3},
        {"text": data["nq_o1"], "score": 1},
        {"text": message.text.strip(), "score": 0},
    ]
    await add_question(vid, "test", data["nq_text"], options=opts)
    await state.clear()
    qs = await get_vacancy_questions(vid)
    await message.answer(
        "✅ <b>Test savoli qo'shildi.</b>\n"
        "<i>Variantlar nomzodga aralashtirilib ko'rsatiladi.</i>",
        parse_mode="HTML",
        reply_markup=questions_list_keyboard(vid, qs))


@router.message(QuestionEditState.new_written, F.text)
async def vq_new_written(message: Message, state: FSMContext):
    from app.question_bank import RUBRIC_LOGIC
    data = await state.get_data()
    vid = data["add_vid"]
    await add_question(vid, "written", message.text.strip(), rubric=RUBRIC_LOGIC)
    await state.clear()
    qs = await get_vacancy_questions(vid)
    await message.answer(
        "✅ <b>Yozma savol qo'shildi.</b>", parse_mode="HTML",
        reply_markup=questions_list_keyboard(vid, qs))


@router.message(QuestionEditState.new_video, F.text)
async def vq_new_video(message: Message, state: FSMContext):
    from app.question_bank import VIDEO_RUBRIC
    data = await state.get_data()
    vid = data["add_vid"]
    await add_question(vid, "video", message.text.strip(), rubric=VIDEO_RUBRIC)
    await state.clear()
    qs = await get_vacancy_questions(vid)
    await message.answer(
        "✅ <b>Video-savol qo'shildi.</b>", parse_mode="HTML",
        reply_markup=questions_list_keyboard(vid, qs))


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
    mx = MAX_TOTAL if app.max_total is None else app.max_total
    color = color_for(app.total_score, mx)
    return (
        f"{color} <b>{STATUS_LABEL.get(app.status, app.status)}</b>\n"
        f"🧠 Test: {_fmt(app.test_score, MAX_TEST)} · "
        f"✍️ Yozma: {_fmt(app.written_score, MAX_WRITTEN)} · "
        f"🎬 Video: {_fmt(app.video_score, MAX_VIDEO)}\n"
        f"⭐️ <b>Jami: {_fmt(app.total_score, mx) if mx else 'baholanmaydi'}</b>"
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
        lines.append(f"➡️ <b>{sc}</b>")
        if a.ai_feedback:
            # AI izohi allaqachon HTML formatida saqlangan
            lines.append(a.ai_feedback)
        lines.append("")
    await _send_long(bot, callback.from_user.id, "\n".join(lines))
    await callback.answer("Yuborildi ✅")


@router.callback_query(lambda c: c.data.startswith("cd:ai:"))
async def cd_ai_summary(callback: CallbackQuery, bot: Bot):
    if not await _guard(callback):
        return
    app = await get_application(_app_id(callback))
    if not app or not app.ai_summary:
        await callback.answer("AI xulosasi yo'q.", show_alert=True)
        return
    await _send_long(bot, callback.from_user.id,
                     f"👤 <b>{esc(app.full_name)}</b> — ariza #{app.id}\n\n"
                     f"{app.ai_summary}")
    await callback.answer("Yuborildi ✅")


@router.callback_query(lambda c: c.data.startswith("cd:regrade:"))
async def cd_regrade(callback: CallbackQuery, bot: Bot):
    """AI bilan qayta baholash (kalit yoki tarmoq xatosi bo'lgan holat uchun)."""
    if not await _guard(callback):
        return
    app_id = _app_id(callback)
    from app.ai_grader import is_enabled, grade_application
    if not is_enabled():
        await callback.answer(
            "AI baholash yoqilmagan. .env ga ANTHROPIC_API_KEY qo'shib, "
            "botni restart qiling.", show_alert=True)
        return
    await callback.answer("🤖 Baholanmoqda… (bir necha soniya)")
    res = await grade_application(app_id)
    app = await get_application(app_id)
    answers = await get_application_answers(app_id)
    written = [a for a in answers if a.qtype == "written"]
    try:
        await callback.message.edit_reply_markup(
            reply_markup=grade_menu_keyboard(app, written, ai_available=True))
    except Exception:
        pass
    if res["graded"] or res["summary"]:
        await callback.message.answer(
            f"🤖 <b>AI baholash tugadi</b>\n"
            f"Yozma javoblar: {res['graded']} ta baholandi\n"
            f"Umumiy xulosa: {'✅ tayyor' if res['summary'] else '❌ chiqmadi'}\n\n"
            f"<i>Natijani ko'rish: «✍️ Yozma» va «🤖 AI xulosasi» tugmalari.</i>",
            parse_mode="HTML")
    else:
        await callback.message.answer(
            "⚠️ AI baholash natija bermadi. Kalit to'g'riligini yoki "
            "internet ulanishini tekshiring.")


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
            reply_markup=grade_menu_keyboard(app, written, ai_available=_ai_on()))
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
            reply_markup=grade_menu_keyboard(app, written, ai_available=_ai_on()))
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
            reply_markup=grade_menu_keyboard(app, written, ai_available=_ai_on()))
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
