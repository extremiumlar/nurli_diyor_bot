from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.database.crud import (
    get_active_vacancies, get_vacancy, create_application, get_admins_by_role
)
from app.keyboards.inline import vacancies_keyboard
from app.keyboards.reply import phone_keyboard, jobseeker_menu
from app.states.application_state import ApplicationState

router = Router()

ALLOWED_MIME = (
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)

EDUCATION_OPTIONS = ["O'rta", "O'rta maxsus", "Oliy (bakalavr)", "Oliy (magistr)", "Boshqa"]


def education_keyboard():
    buttons = [[InlineKeyboardButton(text=e, callback_data=f"edu:{e}")] for e in EDUCATION_OPTIONS]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── Vakansiyalar ko'rish ───────────────────────────────────────────────────

@router.message(F.text == "📋 Mavjud Vakansiyalar")
async def show_vacancies(message: Message):
    vacancies = await get_active_vacancies()
    if not vacancies:
        await message.answer("Hozircha ochiq vakansiyalar yo'q.")
        return
    for v in vacancies:
        text = (
            f"💼 <b>{v.title}</b>\n\n"
            f"📋 Talablar:\n{v.requirements or '—'}\n\n"
            f"🕐 Grafik: {v.schedule or '—'}\n"
            f"💰 Ish haqi: Kelishiladi"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📝 Ariza Topshirish", callback_data=f"apply_vacancy:{v.id}")
        ]])
        await message.answer(text, parse_mode="HTML", reply_markup=kb)


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
        "Bosqichma-bosqich savollarimizga javob bering.\n\n"
        "1️⃣ Ismi-familiyangizni kiriting:",
        parse_mode="HTML"
    )


# ── 1. Ismi-familiya ──────────────────────────────────────────────────────

@router.message(ApplicationState.full_name)
async def app_get_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(ApplicationState.phone)
    await message.answer("2️⃣ Telefon raqamingizni yuboring:", reply_markup=phone_keyboard())


# ── 2. Telefon ────────────────────────────────────────────────────────────

@router.message(ApplicationState.phone, F.contact)
async def app_get_phone_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await _ask_address(message, state)


@router.message(ApplicationState.phone, F.text)
async def app_get_phone_text(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await _ask_address(message, state)


# ── 3. Yashash manzili ────────────────────────────────────────────────────

async def _ask_address(message: Message, state: FSMContext):
    await state.set_state(ApplicationState.address)
    await message.answer(
        "3️⃣ Yashash manzilingizni kiriting:\n"
        "<i>(Shahar/tuman, mahalla)</i>",
        parse_mode="HTML"
    )


@router.message(ApplicationState.address)
async def app_get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(ApplicationState.birthday)
    await message.answer("4️⃣ Tug'ilgan kuningniz va yilingizni kiriting:\n<i>(Masalan: 19.10.2005)</i>", parse_mode="HTML")


# ── 4. Tug'ilgan yili ─────────────────────────────────────────────────────

@router.message(ApplicationState.birthday)
async def app_get_birth_year(message: Message, state: FSMContext):
    from datetime import datetime
    text = message.text.strip()
    try:
        dt = datetime.strptime(text, "%d.%m.%Y")
        if not (1940 <= dt.year <= 2015):
            raise ValueError("yil chegaradan tashqari")
    except ValueError:
        await message.answer(
            "⚠️ Noto'g'ri format!\n"
            "Tug'ilgan kuningizni <b>KK.OO.YYYY</b> ko'rinishida kiriting.\n"
            "<i>Masalan: 19.10.2005</i>",
            parse_mode="HTML"
        )
        return
    await state.update_data(birth_year=text)
    await state.set_state(ApplicationState.education)
    await message.answer("5️⃣ Ma'lumotingizni tanlang:", reply_markup=education_keyboard())


# ── 5. Ma'lumot ───────────────────────────────────────────────────────────

@router.callback_query(ApplicationState.education, lambda c: c.data.startswith("edu:"))
async def app_get_education(callback: CallbackQuery, state: FSMContext):
    edu = callback.data.split(":", 1)[1]
    await state.update_data(education=edu)
    await _ask_vacancy_step(callback.message, state)
    await callback.answer()


# ── 6. Lavozim tanlash (agar oldin tanlanmagan bo'lsa) ───────────────────

async def _ask_vacancy_step(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("vacancy_id"):
        # lavozim allaqachon tanlangan — to'g'ridan-to'g'ri stajga o'tish
        await state.set_state(ApplicationState.experience)
        await message.answer("6️⃣ Ish stajingizni kiriting:\n<i>(Masalan: 3 yil yoki \"Stajsiz\")</i>",
                             parse_mode="HTML")
        return
    vacancies = await get_active_vacancies()
    await state.set_state(ApplicationState.vacancy)
    await message.answer("6️⃣ Qaysi lavozimga ariza topshirmoqchisiz?",
                         reply_markup=vacancies_keyboard(vacancies))


@router.callback_query(ApplicationState.vacancy, lambda c: c.data.startswith("apply:"))
async def app_get_vacancy(callback: CallbackQuery, state: FSMContext):
    vacancy_id = int(callback.data.split(":")[1])
    await state.update_data(vacancy_id=vacancy_id)
    await state.set_state(ApplicationState.experience)
    await callback.message.answer(
        "7️⃣ Ish stajingizni kiriting:\n<i>(Masalan: 3 yil yoki \"Stajsiz\")</i>",
        parse_mode="HTML"
    )
    await callback.answer()


# ── 7. Ish staji ──────────────────────────────────────────────────────────

@router.message(ApplicationState.experience)
async def app_get_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(ApplicationState.cv)
    await message.answer(
        "8️⃣ CV faylingizni yuklang:\n"
        "<i>Qabul qilinadi: PDF yoki DOCX format</i>",
        parse_mode="HTML"
    )


# ── 8. CV fayl ────────────────────────────────────────────────────────────

@router.message(ApplicationState.cv, F.document)
async def app_get_cv(message: Message, state: FSMContext, bot: Bot):
    doc = message.document
    if doc.mime_type not in ALLOWED_MIME:
        await message.answer("❌ Noto'g'ri format! Faqat PDF yoki DOCX fayl yuklang.")
        return

    await state.update_data(cv_file_id=doc.file_id)
    data = await state.get_data()
    await state.clear()

    await create_application(
        user_id=message.from_user.id,
        full_name=data["full_name"],
        phone=data["phone"],
        address=data.get("address"),
        birth_year=data.get("birth_year"),
        education=data.get("education"),
        vacancy_id=data["vacancy_id"],
        experience=data["experience"],
        cv_file_id=data["cv_file_id"]
    )

    vacancy = await get_vacancy(data["vacancy_id"])

    await message.answer(
        "✅ <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        "Tez orada siz bilan bog'lanamiz.",
        parse_mode="HTML",
        reply_markup=jobseeker_menu()
    )

    # HR adminlarga xabar
    notify_text = (
        f"🔔 <b>Yangi ariza!</b>\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📱 Tel: {data['phone']}\n"
        f"🏠 Manzil: {data.get('address') or '—'}\n"
        f"🎂 Tug'ilgan yili: {data.get('birth_year') or '—'}\n"
        f"🎓 Ma'lumot: {data.get('education') or '—'}\n"
        f"💼 Lavozim: {vacancy.title if vacancy else '—'}\n"
        f"📅 Staj: {data['experience']}"
    )
    admins = await get_admins_by_role("hr_admin")
    from app.config import SUPER_ADMIN_ID
    notify_ids = {a.telegram_id for a in admins} | {SUPER_ADMIN_ID}
    for admin_id in notify_ids:
        try:
            await bot.send_message(admin_id, notify_text, parse_mode="HTML")
            await bot.send_document(admin_id, document=data["cv_file_id"],
                                    caption=f"📄 CV — {data['full_name']}")
        except Exception:
            pass


@router.message(ApplicationState.cv)
async def app_cv_wrong(message: Message):
    await message.answer("❌ Iltimos, faqat PDF yoki DOCX fayl yuboring.")
