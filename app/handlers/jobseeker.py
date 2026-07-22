import json
import random

from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
)
from aiogram.fsm.context import FSMContext

from app.database.crud import (
    get_active_vacancies, get_vacancy, create_application, get_all_admins,
    has_applied_today, get_vacancy_questions, count_vacancy_questions,
    create_answer, update_application, get_application_answers,
)
from app.keyboards.reply import main_menu
from app.states.application_state import ApplicationState, ScreeningState

router = Router()

EDUCATION_OPTIONS = ["O'rta", "O'rta maxsus", "Oliy (bakalavr)", "Oliy (magistr)", "Boshqa"]

CANCEL_BTN = "❌ Bekor qilish"
SKIP_BTN   = "⏭ O'tkazib yuborish"


# ── Yordamchi klaviaturalar ────────────────────────────────────────────────

def cancel_keyboard():
    """Har bir bosqichda pastda ko'rinadigan bekor qilish tugmasi."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=CANCEL_BTN)]],
        resize_keyboard=True
    )


def skip_cancel_keyboard():
    """O'tkazib yuborish + bekor qilish."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=SKIP_BTN)],
            [KeyboardButton(text=CANCEL_BTN)],
        ],
        resize_keyboard=True
    )


def phone_cancel_keyboard():
    """Telefon + bekor qilish."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
            [KeyboardButton(text=CANCEL_BTN)],
        ],
        resize_keyboard=True
    )


def education_keyboard():
    buttons = [[InlineKeyboardButton(text=e, callback_data=f"edu:{e}")] for e in EDUCATION_OPTIONS]
    buttons.append([InlineKeyboardButton(text=CANCEL_BTN, callback_data="cancel_application")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def vacancy_cancel_keyboard(vacancies):
    buttons = [
        [InlineKeyboardButton(text=v.title, callback_data=f"apply:{v.id}")]
        for v in vacancies
    ]
    buttons.append([InlineKeyboardButton(text=CANCEL_BTN, callback_data="cancel_application")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── ❌ Bekor qilish — istalgan bosqichda ishlaydi ─────────────────────────

@router.message(StateFilter(ApplicationState, ScreeningState), F.text == CANCEL_BTN)
@router.message(StateFilter(ApplicationState, ScreeningState), Command("cancel"))
async def cancel_application(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Ariza bekor qilindi.\nIstalgan vaqt qayta topshirishingiz mumkin.",
        reply_markup=main_menu()
    )


@router.callback_query(StateFilter(ApplicationState, ScreeningState), lambda c: c.data == "cancel_application")
async def cancel_application_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "❌ Ariza bekor qilindi.\nIstalgan vaqt qayta topshirishingiz mumkin.",
        reply_markup=main_menu()
    )
    await callback.answer()


# ── Vakansiyalar ko'rish ───────────────────────────────────────────────────

@router.message(F.text == "📋 Mavjud Vakansiyalar")
async def show_vacancies(message: Message):
    vacancies = await get_active_vacancies()
    if not vacancies:
        await message.answer("Hozircha ochiq vakansiyalar yo'q.")
        return
    buttons = [
        [InlineKeyboardButton(text=f"💼 {v.title}", callback_data=f"vacancy_detail:{v.id}")]
        for v in vacancies
    ]
    await message.answer(
        "📋 <b>Mavjud vakansiyalar:</b>\nBatafsil ma'lumot uchun bosing:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(lambda c: c.data.startswith("vacancy_detail:"))
async def show_vacancy_detail(callback: CallbackQuery):
    vacancy_id = int(callback.data.split(":")[1])
    v = await get_vacancy(vacancy_id)
    if not v:
        await callback.answer("Vakansiya topilmadi.")
        return
    text = (
        f"💼 <b>{v.title}</b>\n\n"
        f"📋 <b>Talablar:</b>\n{v.requirements or '—'}\n\n"
        f"💰 <b>Ish haqi:</b> {v.salary or 'Kelishiladi'}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Ariza Topshirish", callback_data=f"apply_vacancy:{v.id}")],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back_to_vacancies")]
    ])
    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()


@router.callback_query(lambda c: c.data == "back_to_vacancies")
async def back_to_vacancies(callback: CallbackQuery):
    vacancies = await get_active_vacancies()
    if not vacancies:
        await callback.message.answer("Hozircha ochiq vakansiyalar yo'q.")
        await callback.answer()
        return
    buttons = [
        [InlineKeyboardButton(text=f"💼 {v.title}", callback_data=f"vacancy_detail:{v.id}")]
        for v in vacancies
    ]
    await callback.message.answer(
        "📋 <b>Mavjud vakansiyalar:</b>\nBatafsil ma'lumot uchun bosing:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


# ── Ariza boshlash ─────────────────────────────────────────────────────────

@router.message(F.text == "📝 Ariza Topshirish")
async def apply_start_menu(message: Message, state: FSMContext):
    vacancies = await get_active_vacancies()
    if not vacancies:
        await message.answer("Hozircha ochiq vakansiyalar yo'q.")
        return
    await _start_application(message, state)


@router.callback_query(lambda c: c.data.startswith("apply_vacancy:"))
async def apply_from_vacancy(callback: CallbackQuery, state: FSMContext):
    vacancy_id = int(callback.data.split(":")[1])
    await state.update_data(vacancy_id=vacancy_id)
    await _start_application(callback.message, state)
    await callback.answer()


async def _start_application(message: Message, state: FSMContext):
    await state.set_state(ApplicationState.consent)
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha, roziman", callback_data="appconsent:yes"),
        InlineKeyboardButton(text="❌ Yo'q",        callback_data="appconsent:no"),
    ]])
    await message.answer(
        "📝 <b>Ariza topshirish</b>\n\n"
        "Ariza uchun rahmat! Davom etish uchun biz ism, telefon, ma'lumot va "
        "maosh kutilmangizni yig'amiz. Ma'lumotlaringiz faqat ishga qabul "
        "jarayonida ishlatiladi.\n\n"
        "Rozimisiz?",
        parse_mode="HTML",
        reply_markup=kb
    )


@router.callback_query(ApplicationState.consent, lambda c: c.data == "appconsent:no")
async def app_consent_no(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "Tushunarli. Rozilik bermasangiz, arizani davom ettira olmaymiz.\n"
        "Fikringiz o'zgarsa, istalgan vaqt qayta boshlashingiz mumkin.",
        reply_markup=main_menu()
    )
    await callback.answer()


@router.callback_query(ApplicationState.consent, lambda c: c.data == "appconsent:yes")
async def app_consent_yes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ApplicationState.full_name)
    await callback.message.answer(
        "Rahmat! Boshladik.\n"
        "<i>Bekor qilish uchun pastdagi tugmani bosing.</i>\n\n"
        "1️⃣ Ism-familiyangizni kiriting:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    await callback.answer()


# ── 1. Ism-familiya ───────────────────────────────────────────────────────

@router.message(ApplicationState.full_name)
async def app_get_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(ApplicationState.phone)
    await message.answer(
        "2️⃣ Telefon raqamingizni yuboring:",
        reply_markup=phone_cancel_keyboard()
    )


# ── 2. Telefon ────────────────────────────────────────────────────────────

@router.message(ApplicationState.phone, F.contact)
async def app_get_phone_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await _ask_age(message, state)


@router.message(ApplicationState.phone, F.text)
async def app_get_phone_text(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await _ask_age(message, state)


# ── 3. Yosh ───────────────────────────────────────────────────────────────

async def _ask_age(message: Message, state: FSMContext):
    await state.set_state(ApplicationState.age)
    await message.answer(
        "3️⃣ Yoshingizni kiriting:\n<i>(Masalan: 25)</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


@router.message(ApplicationState.age)
async def app_get_age(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit() or not (10 <= int(text) <= 90):
        await message.answer(
            "⚠️ Yoshingizni faqat raqam bilan kiriting.\n<i>Masalan: 25</i>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return
    await state.update_data(age=int(text))
    await state.set_state(ApplicationState.address)
    await message.answer(
        "4️⃣ Qayerdansiz?\n<i>(Viloyat / shahar / tuman)</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


# ── 4. Qayerdan ───────────────────────────────────────────────────────────

@router.message(ApplicationState.address)
async def app_get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(ApplicationState.languages)
    await message.answer(
        "5️⃣ Qaysi tillarni bilasiz?\n"
        "<i>(Masalan: O'zbek, Rus, Ingliz)</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


# ── 5. Tillar ─────────────────────────────────────────────────────────────

@router.message(ApplicationState.languages)
async def app_get_languages(message: Message, state: FSMContext):
    await state.update_data(languages=message.text)
    await _ask_vacancy_step(message, state)


# ── 6. Lavozim ────────────────────────────────────────────────────────────

async def _ask_vacancy_step(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("vacancy_id"):
        await _ask_past_work(message, state)
        return
    vacancies = await get_active_vacancies()
    await state.set_state(ApplicationState.vacancy)
    await message.answer(
        "6️⃣ Qanday kasbda ishlamoqchisiz?",
        reply_markup=vacancy_cancel_keyboard(vacancies)
    )


@router.callback_query(ApplicationState.vacancy, lambda c: c.data.startswith("apply:"))
async def app_get_vacancy(callback: CallbackQuery, state: FSMContext):
    vacancy_id = int(callback.data.split(":")[1])
    await state.update_data(vacancy_id=vacancy_id)
    await _ask_past_work(callback.message, state)
    await callback.answer()


# ── 7. Qayerda ishlagan ───────────────────────────────────────────────────

async def _ask_past_work(message: Message, state: FSMContext):
    await state.set_state(ApplicationState.past_work)
    await message.answer(
        "7️⃣ Ilgari qayerda ishlagansiz?\n"
        "<i>(Tashkilot nomi, lavozim, davri. Tajribangiz bo'lmasa \"O'tkazib yuborish\" tugmasini bosing.)</i>",
        parse_mode="HTML",
        reply_markup=skip_cancel_keyboard()
    )


@router.message(ApplicationState.past_work)
async def app_get_past_work(message: Message, state: FSMContext):
    value = None if message.text == SKIP_BTN else message.text
    await state.update_data(past_work=value)
    await state.set_state(ApplicationState.education)
    await message.answer(
        "8️⃣ Ma'lumotingizni tanlang:",
        reply_markup=education_keyboard()
    )


# ── 8. Ma'lumot ───────────────────────────────────────────────────────────

@router.callback_query(ApplicationState.education, lambda c: c.data.startswith("edu:"))
async def app_get_education(callback: CallbackQuery, state: FSMContext):
    edu = callback.data.split(":", 1)[1]
    await state.update_data(education=edu)
    await state.set_state(ApplicationState.additional_skills)
    await callback.message.answer(
        "9️⃣ Qo'shimcha bilim va ko'nikmalaringiz bormi?\n"
        "<i>(Masalan: kompyuter dasturlari, haydovchilik guvohnomasi, sertifikatlar va h.k. "
        "Bo'lmasa \"O'tkazib yuborish\" tugmasini bosing.)</i>",
        parse_mode="HTML",
        reply_markup=skip_cancel_keyboard()
    )
    await callback.answer()


# ── 9. Qo'shimcha ko'nikmalar ─────────────────────────────────────────────

@router.message(ApplicationState.additional_skills)
async def app_get_additional_skills(message: Message, state: FSMContext):
    value = None if message.text == SKIP_BTN else message.text
    await state.update_data(additional_skills=value)
    await state.set_state(ApplicationState.photo)
    await message.answer(
        "🔟 O'zingizning rasmingizni yuboring.",
        reply_markup=cancel_keyboard()
    )


# ── 10. Rasm — yakuniy qadam ──────────────────────────────────────────────

@router.message(ApplicationState.photo, F.photo)
async def app_get_photo(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(photo_file_id=message.photo[-1].file_id)
    await _ask_expected_salary(message, state)


@router.message(ApplicationState.photo)
async def app_photo_wrong(message: Message):
    await message.answer(
        "❌ Iltimos, rasm yuboring.",
        reply_markup=cancel_keyboard()
    )


# ── 11. Kutgan maosh ──────────────────────────────────────────────────────

async def _ask_expected_salary(message: Message, state: FSMContext):
    await state.set_state(ApplicationState.expected_salary)
    await message.answer(
        "1️⃣1️⃣ Kutgan oylik maoshingizni yozing:\n"
        "<i>(Masalan: 5 000 000 so'm yoki Kelishiladi)</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


@router.message(ApplicationState.expected_salary)
async def app_get_salary(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(expected_salary=message.text.strip())
    await _create_and_route(message, state, bot)


# ── Arizani yaratish va oqimni yo'naltirish ────────────────────────────────

async def _create_and_route(message: Message, state: FSMContext, bot: Bot):
    """1-bosqich tugadi: arizani yaratadi. Vakansiyada savol bo'lsa 2-bosqichga
    o'tadi, aks holda darhol yakunlaydi (eski xatti-harakat)."""
    data = await state.get_data()

    if await has_applied_today(message.from_user.id, data["vacancy_id"]):
        await state.clear()
        await message.answer(
            "⚠️ Siz bugun bu vakansiyaga allaqachon ariza topshirgansiz.\n"
            "Ertaga qayta urinib ko'ring.",
            reply_markup=main_menu()
        )
        return

    app = await create_application(
        user_id=message.from_user.id,
        full_name=data["full_name"],
        phone=data["phone"],
        address=data.get("address"),
        age=data.get("age"),
        languages=data.get("languages"),
        education=data.get("education"),
        vacancy_id=data["vacancy_id"],
        experience=data.get("past_work"),
        additional_skills=data.get("additional_skills"),
        photo_file_id=data.get("photo_file_id"),
        cv_file_id=None
    )
    await update_application(app.id, expected_salary=data.get("expected_salary"), stage="stage1")
    await state.update_data(app_id=app.id)

    n_questions = await count_vacancy_questions(data["vacancy_id"])
    if n_questions == 0:
        # Savol yo'q — eski oddiy oqim (rasm bilan xabar, guruhga yuborish)
        await _finish_simple(message, state, bot)
        return

    # Savol bor — 2-bosqichga o'tamiz (neytral xabar)
    await message.answer(
        "Ma'lumotlaringiz uchun rahmat! Endi kasbiy savollarga o'tamiz — "
        "bu bir necha daqiqa vaqt oladi.\n"
        "<i>Bekor qilish uchun pastdagi tugmadan foydalaning.</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    await state.update_data(t_idx=0, w_idx=0)
    await _present_test(message, state, bot)


async def _finish_simple(message: Message, state: FSMContext, bot: Bot):
    """Savolsiz vakansiya uchun: darhol yakunlash + adminlar/guruhga rasm bilan xabar."""
    data = await state.get_data()
    await update_application(data["app_id"], stage="done", status="submitted")
    await state.clear()

    vacancy = await get_vacancy(data["vacancy_id"])
    await message.answer(
        "✅ <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        "Tez orada siz bilan bog'lanamiz.",
        parse_mode="HTML",
        reply_markup=main_menu()
    )
    notify_text = (
        f"🔔 <b>Yangi ariza!</b>\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📱 Tel: {data['phone']}\n"
        f"🎂 Yosh: {data.get('age') or '—'}\n"
        f"📍 Qayerdan: {data.get('address') or '—'}\n"
        f"🗣 Tillar: {data.get('languages') or '—'}\n"
        f"💼 Lavozim: {vacancy.title if vacancy else '—'}\n"
        f"💰 Kutgan maosh: {data.get('expected_salary') or '—'}\n"
        f"🏢 Ish tajribasi: {data.get('past_work') or '—'}\n"
        f"🎓 Ma'lumot: {data.get('education') or '—'}\n"
        f"✨ Qo'shimcha ko'nikmalar: {data.get('additional_skills') or '—'}"
    )
    await _notify_admins_and_group(bot, notify_text, data.get("photo_file_id"))


async def _notify_admins_and_group(bot: Bot, notify_text: str, photo_id: str | None):
    """Yangi ariza/nomzod haqida adminlar va arizalar guruhini xabardor qiladi."""
    from app.config import SUPER_ADMIN_ID
    from app.database.crud import get_setting
    from app.utils import send_to_group

    admins = await get_all_admins()
    notify_ids = {a.telegram_id for a in admins} | {SUPER_ADMIN_ID}
    for chat_id in notify_ids:
        try:
            if photo_id:
                await bot.send_photo(chat_id, photo=photo_id, caption=notify_text, parse_mode="HTML")
            else:
                await bot.send_message(chat_id, notify_text, parse_mode="HTML")
        except Exception:
            pass

    group_id_str = await get_setting("apps_group_id")
    if group_id_str:
        try:
            gid = int(group_id_str)
        except ValueError:
            gid = None
        if gid is not None:
            ok, err = await send_to_group(bot, gid, text=notify_text, photo_id=photo_id)
            if not ok:
                try:
                    await bot.send_message(
                        SUPER_ADMIN_ID,
                        f"⚠️ <b>Guruhga yuborilmadi!</b>\n"
                        f"Guruh ID: <code>{gid}</code>\n"
                        f"Xato: <code>{err}</code>\n\n"
                        f"<i>Botni guruhga qo'shing yoki Sozlamalar → Arizalar guruhini qayta o'rnating.</i>",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass


# ══════════════════════════════════════════════════════════════════════════
#  2-BOSQICH — Test va yozma savollar
# ══════════════════════════════════════════════════════════════════════════

async def _present_test(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    t_idx = data.get("t_idx", 0)
    questions = await get_vacancy_questions(data["vacancy_id"], qtype="test")

    if t_idx >= len(questions):
        await _present_written(message, state, bot)
        return

    q = questions[t_idx]
    options = json.loads(q.options) if q.options else []
    order = list(range(len(options)))
    random.shuffle(order)
    scores = [options[i]["score"] for i in order]
    texts  = [options[i]["text"]  for i in order]

    await state.update_data(
        t_idx=t_idx, cur_scores=scores, cur_texts=texts,
        cur_qid=q.id, cur_qtext=q.text, cur_order=q.order_num,
    )
    await state.set_state(ScreeningState.test)

    buttons = [[InlineKeyboardButton(text=t, callback_data=f"scr_t:{pos}")]
               for pos, t in enumerate(texts)]
    await message.answer(
        f"📝 <b>Test savoli {t_idx + 1}</b>\n\n{q.text}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(ScreeningState.test, lambda c: c.data.startswith("scr_t:"))
async def screening_test_answer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    pos = int(callback.data.split(":")[1])
    data = await state.get_data()
    scores = data.get("cur_scores", [])
    texts  = data.get("cur_texts", [])
    if pos < 0 or pos >= len(scores):
        await callback.answer("Xato tanlov.")
        return

    await create_answer(
        application_id=data["app_id"], question_id=data.get("cur_qid"),
        qtype="test", order_num=data.get("cur_order", 0),
        question_text=data.get("cur_qtext"), answer_text=texts[pos],
        score=scores[pos], max_score=3,
    )
    # Tanlangan variantni ko'rsatib qo'yamiz (ball ko'rsatilmaydi)
    try:
        await callback.message.edit_text(
            f"📝 {data.get('cur_qtext')}\n\n✅ Javobingiz: <i>{texts[pos]}</i>",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await state.update_data(t_idx=data.get("t_idx", 0) + 1)
    await callback.answer()
    await _present_test(callback.message, state, bot)


async def _present_written(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    w_idx = data.get("w_idx", 0)
    questions = await get_vacancy_questions(data["vacancy_id"], qtype="written")

    if w_idx >= len(questions):
        await _ask_video(message, state, bot)
        return

    q = questions[w_idx]
    await state.update_data(
        w_idx=w_idx, cur_qid=q.id, cur_qtext=q.text, cur_order=q.order_num,
    )
    await state.set_state(ScreeningState.written)
    await message.answer(
        f"✍️ <b>Yozma savol {w_idx + 1}</b>\n\n{q.text}\n\n"
        "<i>Javobingizni matn ko'rinishida yozing.</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


@router.message(ScreeningState.written, F.text)
async def screening_written_answer(message: Message, state: FSMContext, bot: Bot):
    if message.text == CANCEL_BTN:
        return  # cancel_application handler ushlaydi
    data = await state.get_data()
    await create_answer(
        application_id=data["app_id"], question_id=data.get("cur_qid"),
        qtype="written", order_num=data.get("cur_order", 0),
        question_text=data.get("cur_qtext"), answer_text=message.text,
        score=None, max_score=3,   # HR/AI keyin baholaydi
    )
    await state.update_data(w_idx=data.get("w_idx", 0) + 1)
    await _present_written(message, state, bot)


@router.message(ScreeningState.written)
async def screening_written_wrong(message: Message):
    await message.answer(
        "❌ Iltimos, javobingizni matn ko'rinishida yozing.",
        reply_markup=cancel_keyboard()
    )


# ══════════════════════════════════════════════════════════════════════════
#  3-BOSQICH — Video-vizitka
# ══════════════════════════════════════════════════════════════════════════

async def _ask_video(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(ScreeningState.video)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=SKIP_BTN)], [KeyboardButton(text=CANCEL_BTN)]],
        resize_keyboard=True
    )
    await message.answer(
        "🎥 <b>3-bosqich — Video-vizitka</b>\n\n"
        "40 soniyadan 1 daqiqagacha qisqa video yuboring: o'zingiz va nima uchun "
        "shu sohada ishlamoqchi ekaningiz haqida qisqacha gapiring.\n\n"
        "<i>Hozir imkoniyat bo'lmasa, «⏭ O'tkazib yuborish» tugmasini bosing.</i>",
        parse_mode="HTML",
        reply_markup=kb
    )


@router.message(ScreeningState.video, F.video)
async def screening_get_video(message: Message, state: FSMContext, bot: Bot):
    await _finalize_screening(message, state, bot,
                              video_file_id=message.video.file_id, is_note=False)


@router.message(ScreeningState.video, F.video_note)
async def screening_get_video_note(message: Message, state: FSMContext, bot: Bot):
    await _finalize_screening(message, state, bot,
                              video_file_id=message.video_note.file_id, is_note=True)


@router.message(ScreeningState.video, F.text == SKIP_BTN)
async def screening_skip_video(message: Message, state: FSMContext, bot: Bot):
    await _finalize_screening(message, state, bot, video_file_id=None, is_note=False)


@router.message(ScreeningState.video)
async def screening_video_wrong(message: Message):
    await message.answer(
        "❌ Iltimos, video yuboring yoki «⏭ O'tkazib yuborish» tugmasini bosing.",
    )


async def _finalize_screening(message: Message, state: FSMContext, bot: Bot,
                              video_file_id: str | None, is_note: bool):
    data = await state.get_data()
    app_id = data["app_id"]

    # Test balini hisoblaymiz
    answers = await get_application_answers(app_id)
    test_score = sum((a.score or 0) for a in answers if a.qtype == "test")

    await update_application(
        app_id,
        test_score=test_score,
        video_file_id=video_file_id,
        video_is_note=is_note,
        stage="done",
        status="submitted",
    )
    await state.clear()

    await message.answer(
        "✅ <b>Arizangiz to'liq qabul qilindi va ko'rib chiqilmoqda.</b>\n\n"
        "Natija bo'yicha HR mutaxassisimiz siz bilan tez orada bog'lanadi. "
        "Sabr-toqatingiz uchun rahmat!",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

    vacancy = await get_vacancy(data["vacancy_id"])
    video_line = "✅ bor" if video_file_id else "❌ yo'q"
    notify_text = (
        f"🆕 <b>Yangi nomzod saralashdan o'tdi!</b>\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📱 Tel: {data['phone']}\n"
        f"💼 Lavozim: {vacancy.title if vacancy else '—'}\n"
        f"💰 Kutgan maosh: {data.get('expected_salary') or '—'}\n"
        f"🧪 Test bali: <b>{test_score}/9</b>\n"
        f"🎥 Video: {video_line}\n\n"
        f"<i>Yozma javoblar va video HR panelda baholanadi.\n"
        f"Ariza №{app_id}</i>"
    )
    await _notify_admins_and_group(bot, notify_text, data.get("photo_file_id"))
