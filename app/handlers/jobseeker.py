from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
)
from aiogram.fsm.context import FSMContext

from app.database.crud import (
    get_active_vacancies, get_vacancy, create_application, get_admins_by_role,
    has_applied_today
)
from app.keyboards.reply import main_menu
from app.states.application_state import ApplicationState

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

@router.message(StateFilter(ApplicationState), F.text == CANCEL_BTN)
@router.message(StateFilter(ApplicationState), Command("cancel"))
async def cancel_application(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Ariza bekor qilindi.\nIstalgan vaqt qayta topshirishingiz mumkin.",
        reply_markup=main_menu()
    )


@router.callback_query(StateFilter(ApplicationState), lambda c: c.data == "cancel_application")
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
        f"🕐 <b>Grafik:</b> {v.schedule or '—'}\n"
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
    await state.set_state(ApplicationState.full_name)
    await message.answer(
        "📝 <b>Ariza topshirish</b>\n\n"
        "Bosqichma-bosqich savollarimizga javob bering.\n"
        "<i>Bekor qilish uchun pastdagi tugmani bosing.</i>\n\n"
        "1️⃣ Ism-familiyangizni kiriting:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


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
        "🔟 O'zingizning rasmingizni yuboring.\n"
        "<i>(Agar bo'lmasa \"O'tkazib yuborish\" tugmasini bosing.)</i>",
        parse_mode="HTML",
        reply_markup=skip_cancel_keyboard()
    )


# ── 10. Rasm — yakuniy qadam ──────────────────────────────────────────────

@router.message(ApplicationState.photo, F.photo)
async def app_get_photo(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(photo_file_id=message.photo[-1].file_id)
    await _finalize_application(message, state, bot)


@router.message(ApplicationState.photo, F.text == SKIP_BTN)
async def app_skip_photo(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(photo_file_id=None)
    await _finalize_application(message, state, bot)


@router.message(ApplicationState.photo)
async def app_photo_wrong(message: Message):
    await message.answer(
        "❌ Iltimos, rasm yuboring yoki \"O'tkazib yuborish\" tugmasini bosing.",
        reply_markup=skip_cancel_keyboard()
    )


async def _finalize_application(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if await has_applied_today(message.from_user.id, data["vacancy_id"]):
        await state.clear()
        await message.answer(
            "⚠️ Siz bugun bu vakansiyaga allaqachon ariza topshirgansiz.\n"
            "Ertaga qayta urinib ko'ring.",
            reply_markup=main_menu()
        )
        return

    await state.clear()

    await create_application(
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
        f"🏢 Ish tajribasi: {data.get('past_work') or '—'}\n"
        f"🎓 Ma'lumot: {data.get('education') or '—'}\n"
        f"✨ Qo'shimcha ko'nikmalar: {data.get('additional_skills') or '—'}"
    )
    admins = await get_admins_by_role("hr_admin")
    from app.config import SUPER_ADMIN_ID
    notify_ids = {a.telegram_id for a in admins} | {SUPER_ADMIN_ID}
    photo_id = data.get("photo_file_id")
    for admin_id in notify_ids:
        try:
            if photo_id:
                await bot.send_photo(admin_id, photo=photo_id, caption=notify_text, parse_mode="HTML")
            else:
                await bot.send_message(admin_id, notify_text, parse_mode="HTML")
        except Exception:
            pass
