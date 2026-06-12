from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.config import SUPER_ADMIN_ID
from app.database.crud import (
    get_admin, get_all_admins, add_admin, remove_admin, update_admin_role,
    get_all_projects, get_project, get_project_stages, get_stage,
    create_project, update_project, archive_project, create_stage, update_stage,
    get_all_vacancies, get_vacancy, create_vacancy, toggle_vacancy, delete_vacancy,
    get_applications, get_all_leads,
    get_admins_by_role, get_all_subscribed_users, get_users_by_role
)
from app.keyboards.inline import (
    admin_main_keyboard, admin_projects_keyboard, admin_project_detail_keyboard,
    admin_stages_keyboard, stage_status_keyboard, admin_vacancies_keyboard,
    admin_vacancy_detail_keyboard, vacancy_delete_confirm_keyboard,
    admin_list_keyboard, admin_detail_keyboard, admin_roles_keyboard,
    admin_remove_confirm_keyboard, ROLE_LABELS,
    broadcast_segment_keyboard, confirm_keyboard
)
from app.states.admin_state import (
    AddProjectState, AddStageState, UpdateStagePhotoState,
    AddVacancyState, BroadcastState, AddAdminState, EditAdminState
)

router = Router()


def is_admin_role(role: str, *allowed: str) -> bool:
    return role in allowed or role == "super_admin"


async def get_role(user_id: int) -> str | None:
    if user_id == SUPER_ADMIN_ID:
        return "super_admin"
    admin = await get_admin(user_id)
    return admin.role if admin else None


# ── /admin ─────────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_panel(message: Message):
    role = await get_role(message.from_user.id)
    if not role:
        await message.answer("❌ Sizda admin huquqi yo'q.")
        return
    await message.answer(f"👤 Admin paneli | Rol: <b>{role}</b>", parse_mode="HTML",
                         reply_markup=admin_main_keyboard(role))


@router.callback_query(lambda c: c.data == "admin:back")
async def admin_back(callback: CallbackQuery):
    role = await get_role(callback.from_user.id)
    if not role:
        await callback.answer("❌ Ruxsat yo'q.")
        return
    await callback.message.edit_text(f"👤 Admin paneli | Rol: <b>{role}</b>", parse_mode="HTML",
                                     reply_markup=admin_main_keyboard(role))
    await callback.answer()


# ── Adminlar boshqaruvi ────────────────────────────────────────────────────

@router.message(Command("addadmin"))
async def add_admin_cmd(message: Message):
    if message.from_user.id != SUPER_ADMIN_ID:
        await message.answer("❌ Bu buyruq faqat super admin uchun.")
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Foydalanish: /addadmin <telegram_id> <role>\nRollar: project_admin, hr_admin, sales_admin, super_admin")
        return
    try:
        tid = int(parts[1])
        role = parts[2]
    except ValueError:
        await message.answer("Noto'g'ri telegram_id.")
        return
    await add_admin(tid, full_name="—", role=role, added_by=message.from_user.id)
    await message.answer(f"✅ Admin qo'shildi: {tid} | Rol: {role}")


@router.message(Command("removeadmin"))
async def remove_admin_cmd(message: Message):
    if message.from_user.id != SUPER_ADMIN_ID:
        await message.answer("❌ Bu buyruq faqat super admin uchun.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Foydalanish: /removeadmin <telegram_id>")
        return
    tid = int(parts[1])
    await remove_admin(tid)
    await message.answer(f"✅ Admin o'chirildi: {tid}")


@router.message(Command("stats"))
async def show_stats(message: Message):
    role = await get_role(message.from_user.id)
    if not role:
        await message.answer("❌ Ruxsat yo'q.")
        return
    users = await get_all_subscribed_users()
    projects = await get_all_projects()
    vacancies = await get_all_vacancies()
    leads = await get_all_leads()
    apps = await get_applications()
    await message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: {len(users)}\n"
        f"🏗 Loyihalar: {len(projects)}\n"
        f"💼 Vakansiyalar: {len(vacancies)}\n"
        f"📋 Lidlar: {len(leads)}\n"
        f"📁 Arizalar: {len(apps)}",
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data == "admin:admins")
async def list_admins(callback: CallbackQuery):
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q.")
        return
    admins = await get_all_admins()
    text = f"👥 <b>Adminlar ro'yxati</b> ({len(admins)} ta):"
    await callback.message.answer(text, parse_mode="HTML",
                                   reply_markup=admin_list_keyboard(admins))
    await callback.answer()


# ── Admin detail ───────────────────────────────────────────────────────────

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
    await callback.message.answer(text, parse_mode="HTML",
                                   reply_markup=admin_detail_keyboard(tid))
    await callback.answer()


# ── Admin qo'shish (inline FSM) ────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin_add:start")
async def admin_add_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q.")
        return
    await state.set_state(AddAdminState.telegram_id)
    await callback.message.answer(
        "➕ <b>Yangi admin qo'shish</b>\n\n"
        "Adminning Telegram ID sini kiriting:\n"
        "<i>(Telegram ID ni @userinfobot orqali bilib olish mumkin)</i>",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AddAdminState.telegram_id)
async def admin_add_get_id(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.lstrip("-").isdigit():
        await message.answer("❌ Noto'g'ri format. Raqam kiriting (masalan: 123456789):")
        return
    await state.update_data(new_admin_id=int(text))
    await state.set_state(AddAdminState.role)
    await message.answer("Adminning rolini tanlang:", reply_markup=admin_roles_keyboard("new_admin_role"))


@router.callback_query(AddAdminState.role, lambda c: c.data.startswith("new_admin_role:"))
async def admin_add_set_role(callback: CallbackQuery, state: FSMContext, bot: Bot):
    role = callback.data.split(":")[1]
    data = await state.get_data()
    tid = data["new_admin_id"]
    await state.clear()

    # Telegram dan ismni olishga harakat
    full_name = "—"
    try:
        chat = await bot.get_chat(tid)
        full_name = chat.full_name or "—"
    except Exception:
        pass

    await add_admin(tid, full_name=full_name, role=role, added_by=callback.from_user.id)
    await callback.message.answer(
        f"✅ Admin qo'shildi!\n\n"
        f"🆔 ID: <code>{tid}</code>\n"
        f"📛 Ism: {full_name}\n"
        f"🎭 Rol: {ROLE_LABELS.get(role, role)}",
        parse_mode="HTML"
    )
    await callback.answer()


# ── Admin rolini o'zgartirish ──────────────────────────────────────────────

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
    tid = data["edit_admin_id"]
    await state.clear()
    await update_admin_role(tid, role)
    await callback.message.answer(
        f"✅ Admin <code>{tid}</code> roli yangilandi: {ROLE_LABELS.get(role, role)}",
        parse_mode="HTML"
    )
    await callback.answer()


# ── Admin o'chirish ────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data.startswith("admin_remove:"))
async def admin_remove_ask(callback: CallbackQuery):
    if callback.from_user.id != SUPER_ADMIN_ID:
        await callback.answer("❌ Ruxsat yo'q.")
        return
    tid = int(callback.data.split(":")[1])
    admin = await get_admin(tid)
    name = admin.full_name if admin else tid
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


# ── Loyihalar ──────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin:projects")
async def admin_projects(callback: CallbackQuery):
    role = await get_role(callback.from_user.id)
    if not is_admin_role(role, "project_admin"):
        await callback.answer("❌ Ruxsat yo'q.")
        return
    projects = await get_all_projects()
    await callback.message.edit_text("🏗 Loyihalar:", reply_markup=admin_projects_keyboard(projects))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_project:"))
async def admin_project_detail(callback: CallbackQuery, state: FSMContext):
    role = await get_role(callback.from_user.id)
    if not is_admin_role(role, "project_admin"):
        await callback.answer("❌ Ruxsat yo'q.")
        return
    val = callback.data.split(":")[1]
    if val == "new":
        await state.set_state(AddProjectState.name)
        await callback.message.answer("Yangi loyiha nomi:")
        await callback.answer()
        return
    project_id = int(val)
    project = await get_project(project_id)
    stages = await get_project_stages(project_id)
    stage_text = ""
    if stages:
        icons = {"done": "✅", "in_progress": "🔄", "pending": "⏳"}
        stage_text = "\n\n📊 Bosqichlar:\n" + "\n".join(
            f"{icons.get(s.status, '⏳')} {s.name}" for s in stages
        )
    text = f"🏗 <b>{project.name}</b>\n📍 {project.address or '—'}\n💬 {project.description or '—'}{stage_text}"
    await callback.message.answer(text, parse_mode="HTML",
                                   reply_markup=admin_project_detail_keyboard(project.id, project.active))
    await callback.answer()


# Yangi loyiha FSM
@router.message(AddProjectState.name)
async def new_project_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProjectState.address)
    await message.answer("Loyiha manzili:")


@router.message(AddProjectState.address)
async def new_project_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(AddProjectState.description)
    await message.answer("Loyiha tavsifi:")


@router.message(AddProjectState.description)
async def new_project_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProjectState.photos)
    await message.answer("Loyiha fotolarini yuboring (bitta yoki bir nechta). Tugatgach /done yozing.")


@router.message(AddProjectState.photos, F.photo)
async def new_project_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(f"✅ Foto qabul qilindi ({len(photos)} ta). Yana yuboring yoki /done yozing.")


@router.message(AddProjectState.photos, Command("done"))
async def new_project_done(message: Message, state: FSMContext):
    data = await state.get_data()
    project = await create_project(data["name"], data["address"], data["description"])
    await state.clear()
    await message.answer(f"✅ Loyiha yaratildi: <b>{project.name}</b> (ID: {project.id})", parse_mode="HTML")


# Bosqich qo'shish
@router.callback_query(lambda c: c.data.startswith("admin_add_stage:"))
async def admin_add_stage(callback: CallbackQuery, state: FSMContext):
    project_id = int(callback.data.split(":")[1])
    await state.update_data(project_id=project_id)
    await state.set_state(AddStageState.name)
    await callback.message.answer("Yangi bosqich nomi:")
    await callback.answer()


@router.message(AddStageState.name)
async def new_stage_name(message: Message, state: FSMContext):
    data = await state.get_data()
    stages = await get_project_stages(data["project_id"])
    order_num = len(stages) + 1
    stage = await create_stage(data["project_id"], message.text, order_num)
    await state.clear()
    await message.answer(f"✅ Bosqich qo'shildi: <b>{stage.name}</b>", parse_mode="HTML")


# Bosqich holati yangilash
@router.callback_query(lambda c: c.data.startswith("admin_stage_status:"))
async def admin_stage_status(callback: CallbackQuery):
    project_id = int(callback.data.split(":")[1])
    stages = await get_project_stages(project_id)
    if not stages:
        await callback.message.answer("Bu loyihada bosqichlar yo'q.")
        await callback.answer()
        return
    await callback.message.answer("Qaysi bosqich holatini o'zgartirmoqchisiz?",
                                   reply_markup=admin_stages_keyboard(stages, "admin_change_status"))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_change_status:"))
async def select_stage_for_status(callback: CallbackQuery):
    stage_id = int(callback.data.split(":")[1])
    await callback.message.answer("Yangi holatni tanlang:", reply_markup=stage_status_keyboard(stage_id))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("set_stage_status:"))
async def set_stage_status(callback: CallbackQuery):
    _, stage_id, status = callback.data.split(":")
    stage = await get_stage(int(stage_id))
    await update_stage(int(stage_id), status=status)
    icons = {"done": "✅ Tugallandi", "in_progress": "🔄 Jarayonda", "pending": "⏳ Kutilmoqda"}
    await callback.message.answer(f"✅ <b>{stage.name}</b> holati yangilandi: {icons.get(status)}", parse_mode="HTML")
    await callback.answer()


# Bosqich foto yangilash
@router.callback_query(lambda c: c.data.startswith("admin_stage_photo:"))
async def admin_stage_photo(callback: CallbackQuery, state: FSMContext):
    project_id = int(callback.data.split(":")[1])
    stages = await get_project_stages(project_id)
    if not stages:
        await callback.message.answer("Bu loyihada bosqichlar yo'q.")
        await callback.answer()
        return
    await state.update_data(project_id=project_id)
    await state.set_state(UpdateStagePhotoState.stage)
    await callback.message.answer("Qaysi bosqich uchun foto?",
                                   reply_markup=admin_stages_keyboard(stages, "upd_photo_stage"))
    await callback.answer()


@router.callback_query(UpdateStagePhotoState.stage, lambda c: c.data.startswith("upd_photo_stage:"))
async def upd_photo_select_stage(callback: CallbackQuery, state: FSMContext):
    stage_id = int(callback.data.split(":")[1])
    await state.update_data(stage_id=stage_id)
    await state.set_state(UpdateStagePhotoState.photo)
    await callback.message.answer("📸 Yangi fotoni yuboring:")
    await callback.answer()


@router.message(UpdateStagePhotoState.photo, F.photo)
async def upd_photo_get_photo(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo_file_id=file_id)
    await state.set_state(UpdateStagePhotoState.note)
    await message.answer("💬 Izoh kiriting:")


@router.message(UpdateStagePhotoState.note)
async def upd_photo_get_note(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await update_stage(data["stage_id"], photo_file_id=data["photo_file_id"], note=message.text)
    stage = await get_stage(data["stage_id"])
    await state.clear()
    await message.answer(f"✅ <b>{stage.name}</b> bosqichi yangilandi.", parse_mode="HTML")

    # Obunachilarga xabar
    from app.database.crud import get_project_subscribers, get_user
    subs = await get_project_subscribers(data["project_id"])
    project = await get_project(data["project_id"])
    for sub in subs:
        try:
            from app.keyboards.inline import unsubscribe_keyboard
            await bot.send_photo(
                sub.user_id,
                photo=data["photo_file_id"],
                caption=(
                    f"🔔 <b>{project.name}</b> loyihasida yangilanish!\n\n"
                    f"📌 Bosqich: {stage.name}\n"
                    f"💬 {message.text}"
                ),
                parse_mode="HTML",
                reply_markup=unsubscribe_keyboard(data["project_id"])
            )
        except Exception:
            pass


# Arxivlash
@router.callback_query(lambda c: c.data.startswith("admin_archive:"))
async def admin_archive_project(callback: CallbackQuery):
    project_id = int(callback.data.split(":")[1])
    project = await get_project(project_id)
    new_active = not project.active
    await update_project(project_id, active=new_active)
    status = "faollashtirildi" if new_active else "arxivlandi"
    await callback.message.answer(f"✅ Loyiha {status}: <b>{project.name}</b>", parse_mode="HTML")
    await callback.answer()


# ── Vakansiyalar ───────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin:vacancies")
async def admin_vacancies(callback: CallbackQuery):
    role = await get_role(callback.from_user.id)
    if not is_admin_role(role, "hr_admin"):
        await callback.answer("❌ Ruxsat yo'q.")
        return
    vacancies = await get_all_vacancies()
    await callback.message.edit_text("💼 Vakansiyalar:", reply_markup=admin_vacancies_keyboard(vacancies))
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_vacancy:"))
async def admin_vacancy_detail(callback: CallbackQuery, state: FSMContext):
    val = callback.data.split(":")[1]
    if val == "new":
        await state.set_state(AddVacancyState.title)
        await callback.message.answer("Yangi vakansiya nomi (lavozim):")
        await callback.answer()
        return
    vacancy_id = int(val)
    v = await get_vacancy(vacancy_id)
    text = (
        f"💼 <b>{v.title}</b>\n\n"
        f"📋 Talablar:\n{v.requirements or '—'}\n\n"
        f"🕐 Grafik: {v.schedule or '—'}\n"
        f"Holat: {'🟢 Ochiq' if v.active else '🔴 Yopiq'}"
    )
    await callback.message.answer(text, parse_mode="HTML",
                                   reply_markup=admin_vacancy_detail_keyboard(v.id, v.active))
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
    await callback.message.answer(f"✅ Vakansiya {status}: <b>{v.title}</b>", parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_vacancy_delete:"))
async def vacancy_delete_ask(callback: CallbackQuery):
    vacancy_id = int(callback.data.split(":")[1])
    v = await get_vacancy(vacancy_id)
    if not v:
        await callback.answer("Vakansiya topilmadi.")
        return
    await callback.message.answer(
        f"⚠️ <b>{v.title}</b> vakansiyasini o'chirishni tasdiqlaysizmi?\n\n"
        f"<i>Diqqat: bu vakansiyaga bog'liq barcha arizalar ham o'chib ketadi!</i>",
        parse_mode="HTML",
        reply_markup=vacancy_delete_confirm_keyboard(vacancy_id)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("admin_vacancy_confirm_del:"))
async def vacancy_delete_confirm(callback: CallbackQuery):
    vacancy_id = int(callback.data.split(":")[1])
    v = await get_vacancy(vacancy_id)
    title = v.title if v else vacancy_id
    await delete_vacancy(vacancy_id)
    await callback.message.answer(
        f"🗑 <b>{title}</b> vakansiyasi o'chirildi.",
        parse_mode="HTML"
    )
    await callback.answer()


# ── Arizalar ───────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin:applications")
async def admin_applications(callback: CallbackQuery):
    role = await get_role(callback.from_user.id)
    if not is_admin_role(role, "hr_admin"):
        await callback.answer("❌ Ruxsat yo'q.")
        return
    vacancies = await get_all_vacancies()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [
        [InlineKeyboardButton(text=v.title, callback_data=f"admin_apps:{v.id}")]
        for v in vacancies
    ]
    buttons.append([InlineKeyboardButton(text="📁 Barcha arizalar", callback_data="admin_apps:all")])
    await callback.message.answer("Vakansiya tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
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
    for app in apps[:10]:
        v = await get_vacancy(app.vacancy_id) if app.vacancy_id else None
        text = (
            f"📁 <b>Ariza #{app.id}</b>\n"
            f"👤 {app.full_name}\n"
            f"📱 {app.phone}\n"
            f"💼 {v.title if v else '—'}\n"
            f"📅 Tajriba: {app.experience or '—'}"
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
    await bot.send_document(callback.from_user.id, document=app.cv_file_id,
                            caption=f"CV — {app.full_name}")
    await callback.answer()


# ── Lidlar ─────────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin:leads")
async def admin_leads(callback: CallbackQuery):
    role = await get_role(callback.from_user.id)
    if not is_admin_role(role, "sales_admin"):
        await callback.answer("❌ Ruxsat yo'q.")
        return
    leads = await get_all_leads()
    if not leads:
        await callback.message.answer("Lidlar yo'q.")
        await callback.answer()
        return
    text = "📋 <b>Lidlar ro'yxati:</b>\n\n"
    for lead in leads[:20]:
        proj = await get_project(lead.project_id) if lead.project_id else None
        text += (
            f"#{lead.id} | {lead.full_name} | {lead.phone} | "
            f"{proj.name if proj else '—'} | {lead.created_at.strftime('%d.%m.%Y') if lead.created_at else '—'}\n"
        )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.message(Command("export_leads"))
async def export_leads(message: Message, bot: Bot):
    role = await get_role(message.from_user.id)
    if not is_admin_role(role, "sales_admin"):
        await message.answer("❌ Ruxsat yo'q.")
        return
    leads = await get_all_leads()
    import io, csv
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Ism", "Telefon", "Loyiha ID", "Sana"])
    for lead in leads:
        writer.writerow([lead.id, lead.full_name, lead.phone, lead.project_id or "—",
                         str(lead.created_at)[:10] if lead.created_at else "—"])
    output.seek(0)
    from aiogram.types import BufferedInputFile
    file = BufferedInputFile(output.getvalue().encode("utf-8-sig"), filename="leads.csv")
    await bot.send_document(message.from_user.id, document=file, caption="📤 Lidlar eksporti")


# ── Broadcast ──────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin:broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    role = await get_role(callback.from_user.id)
    if not is_admin_role(role, "sales_admin"):
        await callback.answer("❌ Ruxsat yo'q.")
        return
    await state.set_state(BroadcastState.segment)
    await callback.message.answer("Kimga xabar yubormoqchisiz?", reply_markup=broadcast_segment_keyboard())
    await callback.answer()


@router.callback_query(BroadcastState.segment, lambda c: c.data.startswith("broadcast_seg:"))
async def broadcast_segment(callback: CallbackQuery, state: FSMContext):
    seg = callback.data.split(":")[1]
    await state.update_data(segment=seg)
    await state.set_state(BroadcastState.message)
    await callback.message.answer("📝 Yubormoqchi bo'lgan xabaringizni yozing (matn, rasm yoki video):")
    await callback.answer()


@router.message(BroadcastState.message)
async def broadcast_message(message: Message, state: FSMContext):
    await state.update_data(
        text=message.text or message.caption,
        photo=message.photo[-1].file_id if message.photo else None,
        video=message.video.file_id if message.video else None,
        message_id=message.message_id,
        chat_id=message.chat.id
    )
    await state.set_state(BroadcastState.confirm)
    await message.answer("Xabarni yuborishni tasdiqlaysizmi?", reply_markup=confirm_keyboard())


@router.callback_query(BroadcastState.confirm, lambda c: c.data == "confirm")
async def broadcast_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    seg = data.get("segment", "all")

    if seg == "all":
        users = await get_all_subscribed_users()
    elif seg in ("client", "jobseeker"):
        users = await get_users_by_role(seg)
    else:
        users = await get_all_subscribed_users()

    sent = 0
    failed = 0
    await callback.message.answer(f"📣 Yuborish boshlandi ({len(users)} ta foydalanuvchi)...")

    import asyncio
    for user in users:
        try:
            await bot.copy_message(
                chat_id=user.id,
                from_chat_id=data["chat_id"],
                message_id=data["message_id"]
            )
            sent += 1
        except Exception:
            from app.database.crud import set_user_unsubscribed
            await set_user_unsubscribed(user.id)
            failed += 1
        await asyncio.sleep(0.05)

    await callback.message.answer(f"✅ Broadcast tugadi!\n📤 Yuborildi: {sent}\n❌ Xato: {failed}")
    await callback.answer()


@router.callback_query(BroadcastState.confirm, lambda c: c.data == "cancel")
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Broadcast bekor qilindi.")
    await callback.answer()


# ── Statistika ─────────────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    role = await get_role(callback.from_user.id)
    if role != "super_admin":
        await callback.answer("❌ Ruxsat yo'q.")
        return
    users = await get_all_subscribed_users()
    projects = await get_all_projects()
    vacancies = await get_all_vacancies()
    leads = await get_all_leads()
    apps = await get_applications()
    await callback.message.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: {len(users)}\n"
        f"🏗 Loyihalar: {len(projects)}\n"
        f"💼 Vakansiyalar: {len(vacancies)}\n"
        f"📋 Lidlar: {len(leads)}\n"
        f"📁 Arizalar: {len(apps)}",
        parse_mode="HTML"
    )
    await callback.answer()
