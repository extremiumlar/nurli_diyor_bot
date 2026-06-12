from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from app.database.crud import (
    get_active_projects, get_project, get_project_stages,
    subscribe_user, unsubscribe_user, create_lead, get_admins_by_role
)
from app.keyboards.inline import (
    projects_keyboard, stages_keyboard, contact_project_keyboard,
    skip_keyboard, unsubscribe_keyboard
)
from app.keyboards.reply import phone_keyboard, client_menu
from app.states.lead_state import LeadState

router = Router()


# ── Proyektlar ─────────────────────────────────────────────────────────────

@router.message(F.text == "🏢 Bizning Proyektlar")
async def show_projects(message: Message):
    projects = await get_active_projects()
    if not projects:
        await message.answer("Hozircha loyihalar mavjud emas.")
        return
    await message.answer("📋 Mavjud loyihalarimiz:", reply_markup=projects_keyboard(projects, "view_project"))


@router.callback_query(lambda c: c.data.startswith("view_project:"))
async def view_project(callback: CallbackQuery, bot: Bot):
    project_id = int(callback.data.split(":")[1])
    project = await get_project(project_id)
    if not project:
        await callback.answer("Loyiha topilmadi.")
        return

    status = "✅ Tayyor" if project.status == "completed" else "🔄 Qurilmoqda"
    stages = await get_project_stages(project_id)
    stage_info = ""
    if stages:
        icons = {"done": "✅", "in_progress": "🔄", "pending": "⏳"}
        stage_info = "\n\n📊 Bosqichlar:\n" + "\n".join(
            f"{icons.get(s.status, '⏳')} {s.name}" for s in stages
        )

    text = (
        f"🏗 <b>{project.name}</b>\n"
        f"📍 {project.address or 'Manzil korsatilmagan'}\n"
        f"📌 Holat: {status}"
        f"{stage_info}\n\n"
        f"💬 {project.description or ''}"
    )

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Bog'lanish", callback_data="contact")],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="back_projects")]
    ])

    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()


@router.callback_query(lambda c: c.data == "back_projects")
async def back_to_projects(callback: CallbackQuery):
    projects = await get_active_projects()
    await callback.message.answer("📋 Loyihalar:", reply_markup=projects_keyboard(projects, "view_project"))
    await callback.answer()


# ── Loyiha Bosqichlari ─────────────────────────────────────────────────────

@router.message(F.text == "📊 Loyiha Bosqichlari")
async def show_stages_projects(message: Message):
    projects = await get_active_projects()
    if not projects:
        await message.answer("Hozircha loyihalar mavjud emas.")
        return
    await message.answer("Qaysi loyihaning bosqichlarini ko'rmoqchisiz?",
                         reply_markup=projects_keyboard(projects, "stages_project"))


@router.callback_query(lambda c: c.data.startswith("stages_project:"))
async def show_stages(callback: CallbackQuery):
    project_id = int(callback.data.split(":")[1])
    project = await get_project(project_id)
    stages = await get_project_stages(project_id)
    if not stages:
        await callback.message.answer(f"'{project.name}' loyihasi uchun bosqichlar hali kiritilmagan.")
        await callback.answer()
        return
    await callback.message.answer(
        f"📊 <b>{project.name}</b> bosqichlari:",
        parse_mode="HTML",
        reply_markup=stages_keyboard(stages, project_id)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("stage:"))
async def show_stage_detail(callback: CallbackQuery, bot: Bot):
    from app.database.crud import get_stage
    stage_id = int(callback.data.split(":")[1])
    stage = await get_stage(stage_id)
    if not stage:
        await callback.answer("Bosqich topilmadi.")
        return

    icons = {"done": "✅ Tugallandi", "in_progress": "🔄 Jarayonda", "pending": "⏳ Kutilmoqda"}
    status = icons.get(stage.status, "⏳ Kutilmoqda")
    updated = stage.updated_at.strftime("%d.%m.%Y") if stage.updated_at else "—"

    text = (
        f"📌 <b>{stage.name}</b>\n"
        f"Holat: {status}\n"
        f"Yangilangan: {updated}\n\n"
        f"{stage.note or ''}"
    )

    if stage.photo_file_id:
        await callback.message.answer_photo(
            photo=stage.photo_file_id,
            caption=text,
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(text, parse_mode="HTML")

    await callback.answer()


# ── Yangiliklarga Obuna ────────────────────────────────────────────────────

@router.message(F.text == "🔔 Yangiliklarga Obuna")
async def subscribe_menu(message: Message):
    projects = await get_active_projects()
    if not projects:
        await message.answer("Hozircha loyihalar mavjud emas.")
        return
    await message.answer("Qaysi loyihaga obuna bo'lmoqchisiz?",
                         reply_markup=projects_keyboard(projects, "subscribe"))


@router.callback_query(lambda c: c.data.startswith("subscribe:"))
async def handle_subscribe(callback: CallbackQuery):
    project_id = int(callback.data.split(":")[1])
    project = await get_project(project_id)
    await subscribe_user(callback.from_user.id, project_id)
    await callback.message.answer(
        f"✅ Siz <b>{project.name}</b> loyihasiga muvaffaqiyatli obuna bo'ldingiz!\n"
        f"Har hafta yangilanishlardan xabardor bo'lasiz.",
        parse_mode="HTML",
        reply_markup=unsubscribe_keyboard(project_id)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("unsubscribe:"))
async def handle_unsubscribe(callback: CallbackQuery):
    project_id = int(callback.data.split(":")[1])
    project = await get_project(project_id)
    await unsubscribe_user(callback.from_user.id, project_id)
    await callback.message.answer(f"🔕 Siz <b>{project.name}</b> obunasidan chiqdingiz.", parse_mode="HTML")
    await callback.answer()


# ── Bog'lanish (Lead FSM) ──────────────────────────────────────────────────

@router.message(F.text == "📞 Bog'lanish")
@router.callback_query(lambda c: c.data == "contact")
async def contact_start(update, state: FSMContext):
    msg = update if isinstance(update, Message) else update.message
    await state.set_state(LeadState.full_name)
    await msg.answer("📝 Ismingizni kiriting:")
    if isinstance(update, CallbackQuery):
        await update.answer()


@router.message(LeadState.full_name)
async def lead_get_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(LeadState.phone)
    await message.answer("📱 Telefon raqamingizni yuboring:", reply_markup=phone_keyboard())


@router.message(LeadState.phone, F.contact)
async def lead_get_phone_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await _ask_project(message, state)


@router.message(LeadState.phone, F.text)
async def lead_get_phone_text(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await _ask_project(message, state)


async def _ask_project(message: Message, state: FSMContext):
    from app.keyboards.reply import client_menu
    projects = await get_active_projects()
    await state.set_state(LeadState.project)
    await message.answer(
        "Qaysi loyiha qiziqtiradi?",
        reply_markup=contact_project_keyboard(projects)
    )


@router.callback_query(LeadState.project, lambda c: c.data.startswith("lead_project:"))
async def lead_get_project(callback: CallbackQuery, state: FSMContext):
    project_id = int(callback.data.split(":")[1])
    await state.update_data(project_id=project_id if project_id != 0 else None)
    await state.set_state(LeadState.note)
    await callback.message.answer(
        "💬 Qo'shimcha izoh qoldiring yoki o'tkazib yuboring:",
        reply_markup=skip_keyboard()
    )
    await callback.answer()


@router.message(LeadState.note)
async def lead_get_note_text(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(note=message.text)
    await _save_lead(message, state, bot)


@router.callback_query(LeadState.note, lambda c: c.data == "skip")
async def lead_skip_note(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(note=None)
    await _save_lead(callback.message, state, bot, user_id=callback.from_user.id)
    await callback.answer()


async def _save_lead(message: Message, state: FSMContext, bot: Bot, user_id: int = None):
    data = await state.get_data()
    uid = user_id or message.from_user.id
    lead = await create_lead(
        user_id=uid,
        full_name=data.get("full_name"),
        phone=data.get("phone"),
        project_id=data.get("project_id"),
        note=data.get("note")
    )
    await state.clear()

    await message.answer(
        "✅ Arizangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.",
        reply_markup=client_menu()
    )

    project_name = "—"
    if data.get("project_id"):
        proj = await get_project(data["project_id"])
        if proj:
            project_name = proj.name

    notify_text = (
        f"🔔 <b>Yangi lid!</b>\n"
        f"👤 Ism: {data.get('full_name')}\n"
        f"📱 Tel: {data.get('phone')}\n"
        f"🏗 Loyiha: {project_name}\n"
        f"💬 Izoh: {data.get('note') or '—'}"
    )
    admins = await get_admins_by_role("sales_admin")
    from app.config import SUPER_ADMIN_ID
    notify_ids = {a.telegram_id for a in admins} | {SUPER_ADMIN_ID}
    for admin_id in notify_ids:
        try:
            await bot.send_message(admin_id, notify_text, parse_mode="HTML")
        except Exception:
            pass
