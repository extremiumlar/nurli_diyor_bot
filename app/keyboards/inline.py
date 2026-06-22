from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def subscribe_keyboard(channel_link: str, instagram_url: str | None) -> InlineKeyboardMarkup:
    """Majburiy obuna tugmalari. Instagram URL yo'q bo'lsa — faqat kanal ko'rsatiladi."""
    social_row = [InlineKeyboardButton(text="📢 Telegram kanal", url=channel_link)]
    if instagram_url:
        social_row.append(InlineKeyboardButton(text="📸 Instagram", url=instagram_url))
    return InlineKeyboardMarkup(inline_keyboard=[
        social_row,
        [InlineKeyboardButton(text="✅ Obuna bo'ldim — tekshirish",
                              callback_data="check_subscribe")],
    ])


def not_subscribed_keyboard(channel_link: str, instagram_url: str | None) -> InlineKeyboardMarkup:
    """Faqat Telegram ga obuna bo'lmagan holatda."""
    rows = [[InlineKeyboardButton(text="📢 Telegram kanalga o'tish", url=channel_link)]]
    if instagram_url:
        rows.append([InlineKeyboardButton(text="📸 Instagram", url=instagram_url)])
    rows.append([InlineKeyboardButton(text="✅ Obuna bo'ldim — tekshirish",
                                      callback_data="check_subscribe")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def change_role_keyboard(current_role: str) -> InlineKeyboardMarkup:
    """Foydalanuvchi o'z rolini o'zgartirishi uchun klaviatura."""
    client_mark   = "✅ " if current_role == "client"    else ""
    jobseeker_mark = "✅ " if current_role == "jobseeker" else ""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{client_mark}👤 Mijoz",
            callback_data="role:client"
        )],
        [InlineKeyboardButton(
            text=f"{jobseeker_mark}👷 Ish izlovchi",
            callback_data="role:jobseeker"
        )],
    ])


def role_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👤 Men mijozman", callback_data="role:client"),
        InlineKeyboardButton(text="👷 Ish qidiraman", callback_data="role:jobseeker")
    ]])


def projects_keyboard(projects, prefix="project"):
    buttons = [
        [InlineKeyboardButton(text=p.name, callback_data=f"{prefix}:{p.id}")]
        for p in projects
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def stages_keyboard(stages, project_id):
    status_icon = {"done": "✅", "in_progress": "🔄", "pending": "⏳"}
    buttons = [
        [InlineKeyboardButton(
            text=f"{status_icon.get(s.status, '⏳')} {s.name}",
            callback_data=f"stage:{s.id}"
        )]
        for s in stages
    ]
    buttons.append([InlineKeyboardButton(text="🔔 Obuna bo'lish", callback_data=f"subscribe:{project_id}")])
    buttons.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="back_projects")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def contact_project_keyboard(projects):
    buttons = [
        [InlineKeyboardButton(text=p.name, callback_data=f"lead_project:{p.id}")]
        for p in projects
    ]
    buttons.append([InlineKeyboardButton(text="Aniq loyiha yo'q", callback_data="lead_project:0")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def skip_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⏭️ O'tkazib yuborish", callback_data="skip")
    ]])


def vacancies_keyboard(vacancies, prefix="apply"):
    buttons = [
        [InlineKeyboardButton(text=v.title, callback_data=f"{prefix}:{v.id}")]
        for v in vacancies
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm"),
        InlineKeyboardButton(text="❌ Bekor", callback_data="cancel")
    ]])


def unsubscribe_keyboard(project_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔕 Obunadan chiqish", callback_data=f"unsubscribe:{project_id}")
    ]])


# Admin keyboards
def admin_main_keyboard(role: str):
    """HR ga moslantirilgan admin panel."""
    buttons = [
        [InlineKeyboardButton(text="💼 Vakansiyalar", callback_data="admin:vacancies")],
        [InlineKeyboardButton(text="📁 Arizalar",     callback_data="admin:applications")],
        [InlineKeyboardButton(text="📥 Excel eksport", callback_data="admin:export")],
        [InlineKeyboardButton(text="📊 Statistika",   callback_data="admin:stats")],
    ]
    if role == "super_admin":
        buttons.append([InlineKeyboardButton(text="👥 Adminlar",    callback_data="admin:admins")])
        buttons.append([InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="admin:settings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📡 Kanal o'rnatish",     callback_data="settings:channel")],
        [InlineKeyboardButton(text="📸 Instagram o'rnatish", callback_data="settings:instagram")],
        [InlineKeyboardButton(text="📥 Arizalar guruhi",     callback_data="settings:apps_group")],
        [InlineKeyboardButton(text="🗑 Kanalni o'chirish",   callback_data="settings:clear_channel")],
        [InlineKeyboardButton(text="🗑 Guruhni o'chirish",   callback_data="settings:clear_group")],
        [InlineKeyboardButton(text="◀️ Ortga",               callback_data="admin:back")],
    ])


def admin_projects_keyboard(projects):
    buttons = [
        [InlineKeyboardButton(text=f"{'🟢' if p.active else '🔴'} {p.name}", callback_data=f"admin_project:{p.id}")]
        for p in projects
    ]
    buttons.append([InlineKeyboardButton(text="➕ Yangi loyiha", callback_data="admin_project:new")])
    buttons.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_project_detail_keyboard(project_id: int, active: bool):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Bosqich foto yangilash", callback_data=f"admin_stage_photo:{project_id}")],
        [InlineKeyboardButton(text="📊 Bosqich holati", callback_data=f"admin_stage_status:{project_id}")],
        [InlineKeyboardButton(text="➕ Bosqich qo'shish", callback_data=f"admin_add_stage:{project_id}")],
        [InlineKeyboardButton(
            text="🗄 Arxivlash" if active else "✅ Faollashtirish",
            callback_data=f"admin_archive:{project_id}"
        )],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:projects")]
    ])


def admin_stages_keyboard(stages, prefix="admin_upd_stage"):
    status_icon = {"done": "✅", "in_progress": "🔄", "pending": "⏳"}
    buttons = [
        [InlineKeyboardButton(
            text=f"{status_icon.get(s.status, '⏳')} {s.name}",
            callback_data=f"{prefix}:{s.id}"
        )]
        for s in stages
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def stage_status_keyboard(stage_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tugallandi", callback_data=f"set_stage_status:{stage_id}:done")],
        [InlineKeyboardButton(text="🔄 Jarayonda", callback_data=f"set_stage_status:{stage_id}:in_progress")],
        [InlineKeyboardButton(text="⏳ Kutilmoqda", callback_data=f"set_stage_status:{stage_id}:pending")],
    ])


def admin_vacancies_keyboard(vacancies):
    buttons = [
        [InlineKeyboardButton(
            text=f"{'🟢' if v.active else '🔴'} {v.title}",
            callback_data=f"admin_vacancy:{v.id}"
        )]
        for v in vacancies
    ]
    buttons.append([InlineKeyboardButton(text="➕ Yangi vakansiya", callback_data="admin_vacancy:new")])
    buttons.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_vacancy_detail_keyboard(vacancy_id: int, active: bool):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔴 Yopish" if active else "🟢 Ochish",
            callback_data=f"admin_vacancy_toggle:{vacancy_id}"
        )],
        [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"admin_vacancy_edit:{vacancy_id}")],
        [InlineKeyboardButton(text="📁 Arizalar", callback_data=f"admin_apps:{vacancy_id}")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"admin_vacancy_delete:{vacancy_id}")],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:vacancies")]
    ])


def vacancy_edit_field_keyboard(vacancy_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Nomi", callback_data=f"vedit_field:{vacancy_id}:title")],
        [InlineKeyboardButton(text="📋 Talablar", callback_data=f"vedit_field:{vacancy_id}:requirements")],
        [InlineKeyboardButton(text="💰 Ish haqi", callback_data=f"vedit_field:{vacancy_id}:salary")],
        [InlineKeyboardButton(text="❌ Bekor", callback_data=f"admin_vacancy:{vacancy_id}")],
    ])


def vacancy_delete_confirm_keyboard(vacancy_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"admin_vacancy_confirm_del:{vacancy_id}")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"admin_vacancy:{vacancy_id}")]
    ])


ROLE_LABELS = {
    "project_admin": "🏗 Loyiha admini",
    "hr_admin":      "💼 HR admin",
    "sales_admin":   "📋 Savdo admini",
    "super_admin":   "👑 Super admin",
}


def admin_list_keyboard(admins):
    """Adminlar ro'yxati — har birini bosganda detail ochiladi."""
    buttons = [
        [InlineKeyboardButton(
            text=f"{ROLE_LABELS.get(a.role, a.role)} | {a.full_name or a.telegram_id}",
            callback_data=f"admin_detail:{a.telegram_id}"
        )]
        for a in admins
    ]
    buttons.append([InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="admin_add:start")])
    buttons.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_detail_keyboard(telegram_id: int):
    """Bitta admin uchun — rol o'zgartirish yoki o'chirish."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Rolni o'zgartirish", callback_data=f"admin_edit_role:{telegram_id}")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"admin_remove:{telegram_id}")],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:admins")]
    ])


def admin_roles_keyboard(callback_prefix: str):
    """Rol tanlash klaviaturasi."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏗 Loyiha admini", callback_data=f"{callback_prefix}:project_admin")],
        [InlineKeyboardButton(text="💼 HR admin",      callback_data=f"{callback_prefix}:hr_admin")],
        [InlineKeyboardButton(text="📋 Savdo admini",  callback_data=f"{callback_prefix}:sales_admin")],
        [InlineKeyboardButton(text="👑 Super admin",   callback_data=f"{callback_prefix}:super_admin")],
    ])


def admin_remove_confirm_keyboard(telegram_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"admin_remove_confirm:{telegram_id}")],
        [InlineKeyboardButton(text="❌ Bekor", callback_data=f"admin_detail:{telegram_id}")]
    ])


def broadcast_segment_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Barcha foydalanuvchilar", callback_data="broadcast_seg:all")],
        [InlineKeyboardButton(text="👤 Faqat mijozlar", callback_data="broadcast_seg:client")],
        [InlineKeyboardButton(text="👷 Faqat ish izlovchilar", callback_data="broadcast_seg:jobseeker")],
    ])
