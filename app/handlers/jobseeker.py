import html
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

LETTERS = ["A", "B", "C", "D", "E"]


def esc(v) -> str:
    """Foydalanuvchi kiritgan matnni HTML uchun xavfsiz qiladi."""
    return html.escape(str(v)) if v is not None else "—"


# ── Yordamchi klaviaturalar ────────────────────────────────────────────────

def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=CANCEL_BTN)]],
        resize_keyboard=True
    )


def skip_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=SKIP_BTN)],
            [KeyboardButton(text=CANCEL_BTN)],
        ],
        resize_keyboard=True
    )


def phone_cancel_keyboard():
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


# ── ❌ Bekor qilish — istalgan bosqichda ishlaydi ─────────────────────────

@router.message(StateFilter(ApplicationState, ScreeningState), F.text == CANCEL_BTN)
@router.message(StateFilter(ApplicationState, ScreeningState), Command("cancel"))
async def cancel_application(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Ariza bekor qilindi.\nIstalgan vaqt qayta topshirishingiz mumkin.",
        reply_markup=main_menu()
    )


@router.callback_query(StateFilter(ApplicationState, ScreeningState),
                       lambda c: c.data == "cancel_application")
async def cancel_application_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "❌ Ariza bekor qilindi.\nIstalgan vaqt qayta topshirishingiz mumkin.",
        reply_markup=main_menu()
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════════════════
#  1-BOSQICH — avval VAKANSIYA tanlanadi, keyin ma'lumotlar
# ══════════════════════════════════════════════════════════════════════════

@router.message(StateFilter(None), F.text == "📝 Ariza Topshirish")
async def apply_start_menu(message: Message, state: FSMContext):
    vacancies = await get_active_vacancies()
    if not vacancies:
        await message.answer("Hozircha ochiq vakansiyalar yo'q.")
        return
    await state.clear()
    buttons = [
        [InlineKeyboardButton(text=f"💼 {v.title}", callback_data=f"apply:{v.id}")]
        for v in vacancies
    ]
    buttons.append([InlineKeyboardButton(text=CANCEL_BTN, callback_data="cancel_pick")])
    await message.answer(
        "💼 <b>Qaysi lavozimga ariza topshirasiz?</b>\n\n"
        "<i>Quyidagi ro'yxatdan tanlang:</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(lambda c: c.data == "cancel_pick")
async def cancel_pick(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer("Bekor qilindi.", reply_markup=main_menu())
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("apply:"))
async def apply_pick_vacancy(callback: CallbackQuery, state: FSMContext):
    """Ro'yxatdan lavozim tanlandi."""
    try:
        vacancy_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("Xato tanlov.")
        return
    await _begin_application(callback, state, vacancy_id)


@router.callback_query(lambda c: c.data.startswith("apply_vacancy:"))
async def apply_from_announcement(callback: CallbackQuery, state: FSMContext):
    """E'lon xabaridagi 'Ariza topshirish' tugmasi."""
    try:
        vacancy_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("Xato tanlov.")
        return
    await _begin_application(callback, state, vacancy_id)


async def _begin_application(callback: CallbackQuery, state: FSMContext, vacancy_id: int):
    v = await get_vacancy(vacancy_id)
    if not v or not v.active:
        await callback.answer(
            "❌ Bu vakansiya yopilgan. Iltimos, boshqa lavozimni tanlang.",
            show_alert=True
        )
        return

    # Bugun shu vakansiyaga topshirilganini BOSHIDA tekshiramiz
    if await has_applied_today(callback.from_user.id, vacancy_id):
        await callback.answer(
            "⚠️ Siz bugun bu lavozimga allaqachon ariza topshirgansiz. Ertaga urinib ko'ring.",
            show_alert=True
        )
        return

    # Eski FSM ma'lumotini tozalab, faqat tanlangan vakansiyani qoldiramiz
    await state.set_data({"vacancy_id": vacancy_id, "vacancy_title": v.title})
    await state.set_state(ApplicationState.consent)

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ha, roziman", callback_data="appconsent:yes"),
        InlineKeyboardButton(text="❌ Yo'q",        callback_data="appconsent:no"),
    ]])
    n_q = await count_vacancy_questions(vacancy_id)
    steps = ("Jarayon 3 bosqichdan iborat: ma'lumotlar → kasbiy savollar → qisqa video.\n"
             "Taxminan 10-15 daqiqa vaqt oladi.\n\n") if n_q else ""
    await callback.message.answer(
        f"📝 <b>{esc(v.title)}</b> — ariza topshirish\n\n"
        f"{steps}"
        "Ariza uchun rahmat! Davom etish uchun ism, telefon, ma'lumot va "
        "maosh kutilmangizni yig'amiz. Ma'lumotlaringiz faqat ishga qabul "
        "jarayonida ishlatiladi.\n\n"
        "Rozimisiz?",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()


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

@router.message(ApplicationState.full_name, F.text)
async def app_get_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 3:
        await message.answer("⚠️ Ism-familiyangizni to'liq kiriting.", reply_markup=cancel_keyboard())
        return
    await state.update_data(full_name=name)
    await state.set_state(ApplicationState.phone)
    await message.answer(
        "2️⃣ Telefon raqamingizni yuboring:\n"
        "<i>Pastdagi tugma orqali yuborish qulayroq.</i>",
        parse_mode="HTML",
        reply_markup=phone_cancel_keyboard()
    )


@router.message(ApplicationState.full_name)
async def app_name_wrong(message: Message):
    await message.answer("⚠️ Iltimos, ism-familiyangizni matn ko'rinishida yozing.",
                         reply_markup=cancel_keyboard())


# ── 2. Telefon ────────────────────────────────────────────────────────────

@router.message(ApplicationState.phone, F.contact)
async def app_get_phone_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await _ask_age(message, state)


@router.message(ApplicationState.phone, F.text)
async def app_get_phone_text(message: Message, state: FSMContext):
    raw = message.text.strip()
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not (7 <= len(digits) <= 15):
        await message.answer(
            "⚠️ Telefon raqami noto'g'ri.\n"
            "<i>Masalan: +998901234567</i>\n"
            "Yoki pastdagi tugma orqali yuboring.",
            parse_mode="HTML",
            reply_markup=phone_cancel_keyboard()
        )
        return
    await state.update_data(phone=raw)
    await _ask_age(message, state)


@router.message(ApplicationState.phone)
async def app_phone_wrong(message: Message):
    await message.answer("⚠️ Telefon raqamini yuboring yoki pastdagi tugmani bosing.",
                         reply_markup=phone_cancel_keyboard())


# ── 3. Yosh ───────────────────────────────────────────────────────────────

async def _ask_age(message: Message, state: FSMContext):
    await state.set_state(ApplicationState.age)
    await message.answer(
        "3️⃣ Yoshingizni kiriting:\n<i>(Masalan: 25)</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


@router.message(ApplicationState.age, F.text)
async def app_get_age(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit() or not (16 <= int(text) <= 70):
        await message.answer(
            "⚠️ Yoshingizni faqat raqam bilan kiriting (16-70).\n<i>Masalan: 25</i>",
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


@router.message(ApplicationState.age)
async def app_age_wrong(message: Message):
    await message.answer("⚠️ Yoshingizni raqam bilan yozing.", reply_markup=cancel_keyboard())


# ── 4. Qayerdan ───────────────────────────────────────────────────────────

@router.message(ApplicationState.address, F.text)
async def app_get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text.strip())
    await state.set_state(ApplicationState.languages)
    await message.answer(
        "5️⃣ Qaysi tillarni bilasiz?\n"
        "<i>(Masalan: O'zbek, Rus, Ingliz)</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


@router.message(ApplicationState.address)
async def app_address_wrong(message: Message):
    await message.answer("⚠️ Iltimos, matn ko'rinishida yozing.", reply_markup=cancel_keyboard())


# ── 5. Tillar ─────────────────────────────────────────────────────────────

@router.message(ApplicationState.languages, F.text)
async def app_get_languages(message: Message, state: FSMContext):
    await state.update_data(languages=message.text.strip())
    await _ask_past_work(message, state)


@router.message(ApplicationState.languages)
async def app_languages_wrong(message: Message):
    await message.answer("⚠️ Iltimos, matn ko'rinishida yozing.", reply_markup=cancel_keyboard())


# ── 6. Qayerda ishlagan ───────────────────────────────────────────────────

async def _ask_past_work(message: Message, state: FSMContext):
    await state.set_state(ApplicationState.past_work)
    await message.answer(
        "6️⃣ Ilgari qayerda ishlagansiz?\n"
        "<i>(Tashkilot nomi, lavozim, davri. Tajribangiz bo'lmasa "
        "\"O'tkazib yuborish\" tugmasini bosing.)</i>",
        parse_mode="HTML",
        reply_markup=skip_cancel_keyboard()
    )


@router.message(ApplicationState.past_work, F.text)
async def app_get_past_work(message: Message, state: FSMContext):
    value = None if message.text == SKIP_BTN else message.text.strip()
    await state.update_data(past_work=value)
    await state.set_state(ApplicationState.education)
    await message.answer(
        "7️⃣ Ma'lumotingizni tanlang:",
        reply_markup=education_keyboard()
    )


@router.message(ApplicationState.past_work)
async def app_past_work_wrong(message: Message):
    await message.answer("⚠️ Iltimos, matn yozing yoki tugmani bosing.",
                         reply_markup=skip_cancel_keyboard())


# ── 7. Ma'lumot ───────────────────────────────────────────────────────────

@router.callback_query(ApplicationState.education, lambda c: c.data.startswith("edu:"))
async def app_get_education(callback: CallbackQuery, state: FSMContext):
    edu = callback.data.split(":", 1)[1]
    await state.update_data(education=edu)
    await state.set_state(ApplicationState.additional_skills)
    await callback.message.answer(
        "8️⃣ Qo'shimcha bilim va ko'nikmalaringiz bormi?\n"
        "<i>(Masalan: kompyuter dasturlari, haydovchilik guvohnomasi, sertifikatlar. "
        "Bo'lmasa \"O'tkazib yuborish\" tugmasini bosing.)</i>",
        parse_mode="HTML",
        reply_markup=skip_cancel_keyboard()
    )
    await callback.answer()


# ── 8. Qo'shimcha ko'nikmalar ─────────────────────────────────────────────

@router.message(ApplicationState.additional_skills, F.text)
async def app_get_additional_skills(message: Message, state: FSMContext):
    value = None if message.text == SKIP_BTN else message.text.strip()
    await state.update_data(additional_skills=value)
    await state.set_state(ApplicationState.photo)
    await message.answer(
        "9️⃣ O'zingizning rasmingizni yuboring.\n"
        "<i>Rasm HR uchun ariza kartochkasida ko'rinadi.</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


@router.message(ApplicationState.additional_skills)
async def app_skills_wrong(message: Message):
    await message.answer("⚠️ Iltimos, matn yozing yoki tugmani bosing.",
                         reply_markup=skip_cancel_keyboard())


# ── 9. Rasm ───────────────────────────────────────────────────────────────

@router.message(ApplicationState.photo, F.photo)
async def app_get_photo(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(photo_file_id=message.photo[-1].file_id)
    await _ask_expected_salary(message, state)


@router.message(ApplicationState.photo)
async def app_photo_wrong(message: Message):
    await message.answer("❌ Iltimos, rasm yuboring.", reply_markup=cancel_keyboard())


# ── 10. Kutgan maosh ──────────────────────────────────────────────────────

async def _ask_expected_salary(message: Message, state: FSMContext):
    await state.set_state(ApplicationState.expected_salary)
    await message.answer(
        "🔟 Kutgan oylik maoshingizni yozing:\n"
        "<i>(Masalan: 5 000 000 so'm yoki Kelishiladi)</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


@router.message(ApplicationState.expected_salary, F.text)
async def app_get_salary(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(expected_salary=message.text.strip())
    await _create_and_route(message, state, bot)


@router.message(ApplicationState.expected_salary)
async def app_salary_wrong(message: Message):
    await message.answer("⚠️ Iltimos, matn ko'rinishida yozing.", reply_markup=cancel_keyboard())


# ══════════════════════════════════════════════════════════════════════════
#  Arizani yaratish va oqimni yo'naltirish
# ══════════════════════════════════════════════════════════════════════════

async def _create_and_route(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    vacancy_id = data.get("vacancy_id")
    if not vacancy_id:
        await state.clear()
        await message.answer("⚠️ Ariza ma'lumoti yo'qoldi. Iltimos, qaytadan boshlang.",
                             reply_markup=main_menu())
        return

    app = await create_application(
        user_id=message.from_user.id,
        full_name=data.get("full_name"),
        phone=data.get("phone"),
        address=data.get("address"),
        age=data.get("age"),
        languages=data.get("languages"),
        education=data.get("education"),
        vacancy_id=vacancy_id,
        experience=data.get("past_work"),
        additional_skills=data.get("additional_skills"),
        photo_file_id=data.get("photo_file_id"),
        cv_file_id=None
    )
    await update_application(app.id, expected_salary=data.get("expected_salary"), stage="stage1")
    await state.update_data(app_id=app.id)

    n_questions = await count_vacancy_questions(vacancy_id)
    if n_questions == 0:
        # Savol biriktirilmagan vakansiya — oddiy ariza
        await _finish_simple(message, state, bot)
        return

    await message.answer(
        "✅ Ma'lumotlaringiz uchun rahmat!\n\n"
        "Endi <b>2-bosqich</b> — kasbiy savollarga o'tamiz. "
        "Bu bir necha daqiqa vaqt oladi.",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )
    await state.update_data(t_idx=0, w_idx=0)
    await update_application(app.id, stage="stage2")
    await _present_test(message, state, bot)


async def _finish_simple(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await update_application(data["app_id"], stage="done", status="submitted")
    await state.clear()

    vacancy = await get_vacancy(data["vacancy_id"])
    await message.answer(
        "✅ <b>Arizangiz qabul qilindi!</b>\n\n"
        "Natija bo'yicha HR mutaxassisimiz siz bilan tez orada bog'lanadi.",
        parse_mode="HTML",
        reply_markup=main_menu()
    )
    await _notify_new_candidate(bot, data["app_id"])


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
    if not options:
        await state.update_data(t_idx=t_idx + 1)
        await _present_test(message, state, bot)
        return

    order = list(range(len(options)))
    random.shuffle(order)
    scores = [options[i]["score"] for i in order]
    texts  = [options[i]["text"]  for i in order]

    await state.update_data(
        t_idx=t_idx, cur_scores=scores, cur_texts=texts,
        cur_qid=q.id, cur_qtext=q.text, cur_order=q.order_num,
    )
    await state.set_state(ScreeningState.test)

    # Variant matnlari uzun — ular XABAR ichida ko'rsatiladi,
    # tugmalarda faqat harf (A/B/C) turadi. Aks holda matn tugmaga sig'maydi.
    body = "\n\n".join(f"<b>{LETTERS[i]})</b> {esc(t)}" for i, t in enumerate(texts))
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=LETTERS[i], callback_data=f"scr_t:{i}")
        for i in range(len(texts))
    ]])
    await message.answer(
        f"🧠 <b>Test savoli {t_idx + 1}/{len(questions)}</b>\n\n"
        f"{esc(q.text)}\n\n{body}\n\n"
        f"<i>Javobingizni tanlang:</i>",
        parse_mode="HTML",
        reply_markup=kb
    )


@router.callback_query(ScreeningState.test, lambda c: c.data.startswith("scr_t:"))
async def screening_test_answer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        pos = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("Xato tanlov.")
        return

    data = await state.get_data()
    scores = data.get("cur_scores", [])
    texts  = data.get("cur_texts", [])
    if pos < 0 or pos >= len(scores):
        await callback.answer("Xato tanlov.")
        return

    # Takroriy bosishdan himoya: shu savolga javob allaqachon yozilganmi?
    answers = await get_application_answers(data["app_id"])
    if any(a.question_id == data.get("cur_qid") for a in answers):
        await callback.answer("Bu savolga javob berilgan.")
        return

    await create_answer(
        application_id=data["app_id"], question_id=data.get("cur_qid"),
        qtype="test", order_num=data.get("cur_order", 0),
        question_text=data.get("cur_qtext"), answer_text=texts[pos],
        score=scores[pos], max_score=3,
    )
    try:
        await callback.message.edit_text(
            f"🧠 {esc(data.get('cur_qtext'))}\n\n"
            f"✅ <b>Javobingiz:</b> {LETTERS[pos]}) {esc(texts[pos])}",
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
    await state.update_data(w_idx=w_idx, cur_qid=q.id, cur_qtext=q.text, cur_order=q.order_num)
    await state.set_state(ScreeningState.written)
    await message.answer(
        f"✍️ <b>Yozma savol {w_idx + 1}/{len(questions)}</b>\n\n"
        f"{esc(q.text)}\n\n"
        "<i>Javobingizni bitta xabar qilib yozing.</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


@router.message(ScreeningState.written, F.text)
async def screening_written_answer(message: Message, state: FSMContext, bot: Bot):
    text = message.text.strip()
    if len(text) < 10:
        await message.answer(
            "⚠️ Javobingiz juda qisqa. Iltimos, biroz batafsilroq yozing.",
            reply_markup=cancel_keyboard()
        )
        return
    data = await state.get_data()
    await create_answer(
        application_id=data["app_id"], question_id=data.get("cur_qid"),
        qtype="written", order_num=data.get("cur_order", 0),
        question_text=data.get("cur_qtext"), answer_text=text,
        score=None, max_score=3,
    )
    await state.update_data(w_idx=data.get("w_idx", 0) + 1)
    await _present_written(message, state, bot)


@router.message(ScreeningState.written)
async def screening_written_wrong(message: Message):
    await message.answer("⚠️ Iltimos, javobingizni matn ko'rinishida yozing.",
                         reply_markup=cancel_keyboard())


# ══════════════════════════════════════════════════════════════════════════
#  3-BOSQICH — MAJBURIY video
# ══════════════════════════════════════════════════════════════════════════

async def _ask_video(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await update_application(data["app_id"], stage="stage3")
    await state.set_state(ScreeningState.video)

    vqs = await get_vacancy_questions(data["vacancy_id"], qtype="video")
    video_q = vqs[0].text if vqs else "Nega aynan shu lavozimda ishlamoqchisiz?"

    await message.answer(
        "🎥 <b>Oxirgi bosqich — qisqa video (30-60 soniya)</b>\n\n"
        "Avval o'zingizni qisqacha tanishtiring (~10 soniya), so'ng savolga javob bering:\n\n"
        f"❓ <b>{esc(video_q)}</b>\n\n"
        "🔵 Xohlasangiz <b>yumaloq video-xabar</b>, xohlasangiz <b>oddiy video</b> "
        "yuborishingiz mumkin — ikkalasi ham bo'ladi.\n\n"
        "⚠️ <b>Video majburiy.</b> Videosiz arizangiz HR mutaxassisiga "
        "yuborilmaydi va ko'rib chiqilmaydi.",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


@router.message(ScreeningState.video, F.video)
async def screening_get_video(message: Message, state: FSMContext, bot: Bot):
    await _finalize_screening(message, state, bot,
                              video_file_id=message.video.file_id, is_note=False)


@router.message(ScreeningState.video, F.video_note)
async def screening_get_video_note(message: Message, state: FSMContext, bot: Bot):
    await _finalize_screening(message, state, bot,
                              video_file_id=message.video_note.file_id, is_note=True)


@router.message(ScreeningState.video)
async def screening_video_wrong(message: Message):
    await message.answer(
        "❌ Bu video emas.\n\n"
        "Iltimos, <b>video</b> yoki <b>yumaloq video-xabar</b> yuboring "
        "(30-60 soniya).\n\n"
        "⚠️ Videosiz arizangiz HRga yuborilmaydi.",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


async def _finalize_screening(message: Message, state: FSMContext, bot: Bot,
                              video_file_id: str, is_note: bool):
    data = await state.get_data()
    app_id = data.get("app_id")
    if not app_id:
        await state.clear()
        await message.answer("⚠️ Ariza ma'lumoti yo'qoldi. Qaytadan boshlang.",
                             reply_markup=main_menu())
        return

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

    # AI baholash (kalit bo'lsa) — yozma javoblarga ball qo'yadi va xulosa yozadi.
    # Xato bo'lsa oqim buzilmaydi, HR shunchaki qo'lda baholaydi.
    try:
        from app.ai_grader import is_enabled, grade_application
        if is_enabled():
            await grade_application(app_id)
    except Exception:
        pass

    await _notify_new_candidate(bot, app_id)


# ══════════════════════════════════════════════════════════════════════════
#  HR va guruhga xabar — harakat tugmalari bilan
# ══════════════════════════════════════════════════════════════════════════

async def _notify_new_candidate(bot: Bot, app_id: int):
    """Yangi nomzod haqida adminlar va arizalar guruhini xabardor qiladi.
    Xabar ostida to'g'ridan-to'g'ri harakat tugmalari bo'ladi."""
    from app.config import SUPER_ADMIN_ID
    from app.database.crud import get_setting, get_application
    from app.keyboards.inline import candidate_actions_keyboard
    from app.utils import send_to_group

    app = await get_application(app_id)
    if not app:
        return
    vacancy = await get_vacancy(app.vacancy_id) if app.vacancy_id else None

    text = (
        f"🆕 <b>Yangi nomzod</b> — ariza #{app.id}\n\n"
        f"👤 <a href=\"tg://user?id={app.user_id}\">{esc(app.full_name)}</a>\n"
        f"📱 {esc(app.phone)}\n"
        f"💼 {esc(vacancy.title if vacancy else '—')}\n"
        f"🎂 Yosh: {esc(app.age)}\n"
        f"📍 {esc(app.address)}\n"
        f"🗣 {esc(app.languages)}\n"
        f"🎓 {esc(app.education)}\n"
        f"🏢 Tajriba: {esc(app.experience)}\n"
        f"✨ Ko'nikmalar: {esc(app.additional_skills)}\n"
        f"💰 Kutgan maosh: {esc(app.expected_salary)}\n"
    )
    if app.test_score is not None:
        text += f"\n🧠 <b>Test bali: {app.test_score}/9</b>"
    if app.written_score is not None:
        text += f"\n✍️ <b>Yozma (AI): {app.written_score}/6</b>"
    if app.ai_summary:
        # Xulosaning birinchi qatori — tavsiya darajasi (🟢/🟡/🔴)
        head = app.ai_summary.split("\n", 1)[0].replace("🤖 <b>AI xulosasi</b> — ", "")
        text += f"\n🤖 <b>AI tavsiyasi:</b> {head}"
    text += "\n\n<i>Quyidagi tugmalar orqali boshqaring:</i>"

    kb = candidate_actions_keyboard(app)

    # 1) Adminlar (shaxsiy chat)
    admins = await get_all_admins()
    notify_ids = {a.telegram_id for a in admins} | {SUPER_ADMIN_ID}
    for chat_id in notify_ids:
        try:
            if app.photo_file_id:
                await bot.send_photo(chat_id, photo=app.photo_file_id,
                                     caption=text, parse_mode="HTML", reply_markup=kb)
            else:
                await bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass

    # 2) Arizalar guruhi
    group_id_str = await get_setting("apps_group_id")
    if not group_id_str:
        return
    try:
        gid = int(group_id_str)
    except ValueError:
        return
    ok, err = await send_to_group(bot, gid, text=text,
                                  photo_id=app.photo_file_id, reply_markup=kb)
    if not ok:
        try:
            await bot.send_message(
                SUPER_ADMIN_ID,
                f"⚠️ <b>Guruhga yuborilmadi!</b>\n"
                f"Guruh ID: <code>{gid}</code>\nXato: <code>{esc(err)}</code>",
                parse_mode="HTML"
            )
        except Exception:
            pass
