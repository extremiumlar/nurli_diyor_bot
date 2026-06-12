from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.config import SUPER_ADMIN_ID
from app.database.crud import (
    get_admin, get_all_admins, add_admin, remove_admin, update_admin_role,
    get_all_vacancies, get_vacancy, create_vacancy, toggle_vacancy, delete_vacancy,
    get_applications, get_all_subscribed_users,
)
from app.keyboards.inline import (
    admin_main_keyboard,
    admin_vacancies_keyboard, admin_vacancy_detail_keyboard, vacancy_delete_confirm_keyboard,
    admin_list_keyboard, admin_detail_keyboard, admin_roles_keyboard,
    admin_remove_confirm_keyboard, ROLE_LABELS,
)
from app.states.admin_state import AddVacancyState, AddAdminState, EditAdminState

router = Router()


async def get_role(user_id: int) -> str | None:
    if user_id == SUPER_ADMIN_ID:
        return "super_admin"
    admin = await get_admin(user_id)
    return admin.role if admin else None


def is_hr(role: str) -> bool:
    return role in ("hr_admin", "super_admin")


# ── /admin ─────────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_panel(message: Message):
    role = await get_role(message.from_user.id)
    if not role:
        await message.answer("❌ Sizda admin huquqi yo'q.")
        return
    await message.answer(
        f"👤 Admin paneli | Rol: <b>{role}</b>",
        parse_mode="HTML",
        reply_markup=admin_main_keyboard(role)
    )


@router.callback_query(lambda c: c.data == "admin:back")
async def admin_back(callback: CallbackQuery):
    role = await get_role(callback.from_user.id)
    if not role:
        await callback.answer("❌ Ruxsat yo'q.")
        return
    await callback.message.edit_text(
        f"👤 Admin paneli | Rol: <b>{role}</b>",
        parse_mode="HTML",
        reply_markup=admin_main_keyboard(role)
    )
    await callback.answer()


# ── Statistika ─────────────────────────────────────────────────────────────

@router.message(Command("stats"))
@router.callback_query(lambda c: c.data == "admin:stats")
async def show_stats(update, **kwargs):
    msg = update if isinstance(update, Message) else update.message
    uid = update.from_user.id
    role = await get_role(uid)
    if not role:
        await msg.answer("❌ Ruxsat yo'q.")
        return
    users     = await get_all_subscribed_users()
    vacancies = await get_all_vacancies()
    apps      = await get_applications()
    await msg.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: {len(users)}\n"
        f"💼 Vakansiyalar: {len(vacancies)}\n"
        f"📁 Arizalar: {len(apps)}",
        parse_mode="HTML"
    )
    if isinstance(update, CallbackQuery):
        await update.answer()


# ── Vakansiyalar ───────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin:vacancies")
async def admin_vacancies(callback: CallbackQuery):
    role = await get_role(callback.from_user.id)
    if not is_hr(role):
        await callback.answer("❌ Ruxsat yo'q.")
        return
    vacancies = await get_all_vacancies()
    await callback.message.edit_text(
        "💼 Vakansiyalar:",
        reply_markup=admin_vacancies_keyboard(vacancies)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_vacancy:"))
async def admin_vacancy_detail(callback: CallbackQuery, state: FSMContext):
    role = await get_role(callback.from_user.id)
    if not is_hr(role):
        await callback.answer("❌ Ruxsat yo'q.")
        return
    val = callback.data.split(":")[1]
    if val == "new":
        await state.set_state(AddVacancyState.title)
        await callback.message.answer("Yangi vakansiya nomi (lavozim):")
        await callback.answer()
        return
    v = await get_vacancy(int(val))
    text = (
        f"💼 <b>{v.title}</b>\n\n"
        f"📋 Talablar:\n{v.requirements or '—'}\n\n"
        f"🕐 Grafik: {v.schedule or '—'}\n"
        f"Holat: {'🟢 Ochiq' if v.active else '🔴 Yopiq'}"
    )
    await callback.message.answer(
        text, parse_mode="HTML",
        reply_markup=admin_vacancy_detail_keyboard(v.id, v.active)
    )
    await callback.answer()


@router.message(AddVacancyState.title)
async def new_vacancy_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddVacancyState.requirements)
    await message.answer("📋 Talablarni kiriting:")


@router.message(AddVacancyState.requirements)
async def new_vacancy_req(message: Message, state: FSMContext):
    await state.update_data(requirements=message.text)
    await state.set_state(AddVacancyState.schedule)
    await message.answer("🕐 Ish grafigini kiriting:")


@router.message(AddVacancyState.schedule)
async def new_vacancy_schedule(message: Message, state: FSMContext):
    data = await state.get_data()
    v = await create_vacancy(data["title"], data["requirements"], message.text)
    await state.clear()
    await message.answer(f"✅ Vakansiya yaratildi: <b>{v.title}</b>", parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith("admin_vacancy_toggle:"))
async def toggle_vac(callback: CallbackQuery):
    vacancy_id = int(callback.data.split(":")[1])
    v = await get_vacancy(vacancy_id)
    await toggle_vacancy(vacancy_id, not v.active)
    status = "ochildi" if not v.active else "yopildi"
    await callback.message.answer(
        f"✅ Vakansiya {status}: <b>{v.title}</b>", parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_vacancy_delete:"))
async def vacancy_delete_ask(callback: CallbackQuery):
    v = await get_vacancy(int(callback.data.split(":")[1]))
    await callback.message.answer(
        f"⚠️ <b>{v.title}</b> vakansiyasini o'chirishni tasdiqlaysizmi?\n"
        f"<i>Bog'liq barcha arizalar ham o'chadi!</i>",
        parse_mode="HTML",
        reply_markup=vacancy_delete_confirm_keyboard(v.id)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_vacancy_confirm_del:"))
async def vacancy_delete_confirm(callback: CallbackQuery):
    vacancy_id = int(callback.data.split(":")[1])
    v = await get_vacancy(vacancy_id)
    title = v.title if v else vacancy_id
    await delete_vacancy(vacancy_id)
    await callback.message.answer(f"🗑 <b>{title}</b> o'chirildi.", parse_mode="HTML")
    await callback.answer()


# ── Arizalar ───────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin:applications")
async def admin_applications(callback: CallbackQuery):
    role = await get_role(callback.from_user.id)
    if not is_hr(role):
        await callback.answer("❌ Ruxsat yo'q.")
        return
    vacancies = await get_all_vacancies()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [
        [InlineKeyboardButton(text=v.title, callback_data=f"admin_apps:{v.id}")]
        for v in vacancies
    ]
    buttons.append([InlineKeyboardButton(text="📁 Barcha arizalar", callback_data="admin_apps:all")])
    await callback.message.answer(
        "Vakansiya tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_apps:"))
async def show_applications(callback: CallbackQuery, bot: Bot):
    val = callback.data.split(":")[1]
    vid = None if val == "all" else int(val)
    apps = await get_applications(vid)
    if not apps:
        await callback.message.answer("Arizalar yo'q.")
        await callback.answer()
        return
    for app in apps[:15]:
        v = await get_vacancy(app.vacancy_id) if app.vacancy_id else None
        text = (
            f"📁 <b>Ariza #{app.id}</b>\n"
            f"👤 {app.full_name}\n"
            f"📱 {app.phone}\n"
            f"🏠 Manzil: {app.address or '—'}\n"
            f"🎂 Tug'ilgan: {app.birth_year or '—'}\n"
            f"🎓 Ma'lumot: {app.education or '—'}\n"
            f"💼 Lavozim: {v.title if v else '—'}\n"
            f"📅 Staj: {app.experience or '—'}"
        )
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📄 CV ko'rish", callback_data=f"get_cv:{app.id}")
        ]])
        await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("get_cv:"))
async def get_cv(callback: CallbackQuery, bot: Bot):
    app_id = int(callback.data.split(":")[1])
    apps = await get_applications()
    app = next((a for a in apps if a.id == app_id), None)
    if not app or not app.cv_file_id:
        await callback.answer("CV topilmadi.")
        return
    await bot.send_document(
        callback.from_user.id,
        document=app.cv_file_id,
        caption=f"📄 CV — {app.full_name}"
    )
    await callback.answer()


# ── Adminlar boshqaruvi ────────────────────────────────────────────────────

@router.message(Command("addadmin"))
async def add_admin_cmd(message: Message):
    if message.from_user.id != SUPER_ADMIN_ID:
        await message.answer("❌ Faqat super admin uchun.")
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Foydalanish: /addadmin <telegram_id> <role>\nRollar: hr_admin, super_admin")
        return
    try:
        tid, role = int(parts[1]), parts[2]
    except ValueError:
        await message.answer("Noto'g'ri telegram_id.")
        return
    await add_admin(tid, full_name="—", role=role, added_by=message.from_user.id)
    await message.answer(f"✅ Admin qo'shildi: {tid} | Rol: {role}")


@router.message(Command("removeadmin"))
async def remove_admin_cmd(message: Message):
    if message.from_user.id != SUPER_ADMIN_ID:
        await message.answer("❌ Faqat super admin uchun.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Foydalanish: /removeadmin <telegram_id>")
        return
    await remove_admin(int(parts[1]))
    await message.answer(f"✅ Admin o'chirildi: {parts[1]}")


@router.callback_query(lambda c: c.data == "admin:admins")
async def list_admins(callback: CallbackQuery):
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q.")
        return
    admins = await get_all_admins()
    await callback.message.answer(
        f"👥 <b>Adminlar ro'yxati</b> ({len(admins)} ta):",
        parse_mode="HTML",
        reply_markup=admin_list_keyboard(admins)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_detail:"))
async def admin_detail(callback: CallbackQuery):
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q.")
        return
    tid = int(callback.data.split(":")[1])
    admin = await get_admin(tid)
    if not admin:
        await callback.answer("Admin topilmadi.")
        return
    text = (
        f"👤 <b>Admin ma'lumotlari</b>\n\n"
        f"🆔 ID: <code>{admin.telegram_id}</code>\n"
        f"📛 Ism: {admin.full_name or '—'}\n"
        f"🎭 Rol: {ROLE_LABELS.get(admin.role, admin.role)}\n"
        f"📅 Qo'shilgan: {str(admin.created_at)[:10] if admin.created_at else '—'}"
    )
    await callback.message.answer(
        text, parse_mode="HTML",
        reply_markup=admin_detail_keyboard(tid)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "admin_add:start")
async def admin_add_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q.")
        return
    await state.set_state(AddAdminState.telegram_id)
    await callback.message.answer(
        "➕ <b>Yangi admin qo'shish</b>\n\n"
        "Admin Telegram ID sini kiriting:\n"
        "<i>(@userinfobot orqali bilib olish mumkin)</i>",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AddAdminState.telegram_id)
async def admin_add_get_id(message: Message, state: FSMContext):
    if not message.text.strip().lstrip("-").isdigit():
        await message.answer("❌ Raqam kiriting (masalan: 123456789):")
        return
    await state.update_data(new_admin_id=int(message.text.strip()))
    await state.set_state(AddAdminState.role)
    await message.answer("Rolni tanlang:", reply_markup=admin_roles_keyboard("new_admin_role"))


@router.callback_query(AddAdminState.role, lambda c: c.data.startswith("new_admin_role:"))
async def admin_add_set_role(callback: CallbackQuery, state: FSMContext, bot: Bot):
    role = callback.data.split(":")[1]
    data = await state.get_data()
    tid  = data["new_admin_id"]
    await state.clear()
    full_name = "—"
    try:
        chat = await bot.get_chat(tid)
        full_name = chat.full_name or "—"
    except Exception:
        pass
    await add_admin(tid, full_name=full_name, role=role, added_by=callback.from_user.id)
    await callback.message.answer(
        f"✅ Admin qo'shildi!\n"
        f"🆔 <code>{tid}</code> | {full_name} | {ROLE_LABELS.get(role, role)}",
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_edit_role:"))
async def admin_edit_role_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q.")
        return
    tid = int(callback.data.split(":")[1])
    await state.update_data(edit_admin_id=tid)
    await state.set_state(EditAdminState.role)
    await callback.message.answer(
        f"Yangi rolni tanlang (ID: <code>{tid}</code>):",
        parse_mode="HTML",
        reply_markup=admin_roles_keyboard("set_admin_role")
    )
    await callback.answer()


@router.callback_query(EditAdminState.role, lambda c: c.data.startswith("set_admin_role:"))
async def admin_edit_role_confirm(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split(":")[1]
    data = await state.get_data()
    await state.clear()
    await update_admin_role(data["edit_admin_id"], role)
    await callback.message.answer(
        f"✅ Rol yangilandi: {ROLE_LABELS.get(role, role)}", parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_remove:"))
async def admin_remove_ask(callback: CallbackQuery):
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q.")
        return
    tid   = int(callback.data.split(":")[1])
    admin = await get_admin(tid)
    name  = admin.full_name if admin else tid
    await callback.message.answer(
        f"⚠️ <b>{name}</b> adminni o'chirishni tasdiqlaysizmi?",
        parse_mode="HTML",
        reply_markup=admin_remove_confirm_keyboard(tid)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_remove_confirm:"))
async def admin_remove_confirm(callback: CallbackQuery):
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q.")
        return
    tid = int(callback.data.split(":")[1])
    await remove_admin(tid)
    await callback.message.answer(f"✅ Admin <code>{tid}</code> o'chirildi.", parse_mode="HTML")
    await callback.answer()
