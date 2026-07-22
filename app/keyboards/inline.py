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
        [InlineKeyboardButton(text="🎯 Saralash (reyting)", callback_data="scr:menu")],
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
        [InlineKeyboardButton(text="🧪 Guruhni tekshirish",  callback_data="settings:test_group")],
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
    buttons.append([InlineKeyboardButton(text="📢 Guruhga yuborish", callback_data="vac_post:menu")])
    buttons.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def vacancy_post_menu_keyboard(vacancies):
    """Guruhga yuborish menyusi: Barcha faollar yoki bittasini tanlash."""
    buttons = [
        [InlineKeyboardButton(text="📁 Barcha faol vakansiyalar", callback_data="vac_post:all")]
    ]
    for v in vacancies:
        if not v.active:
            continue
        buttons.append([InlineKeyboardButton(
            text=f"💼 {v.title}",
            callback_data=f"vac_post:one:{v.id}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:vacancies")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def applications_post_menu_keyboard(vacancies):
    """Arizalarni guruhga yuborish: Barcha yoki ma'lum vakansiya bo'yicha."""
    buttons = [
        [InlineKeyboardButton(text="📁 Barcha arizalar", callback_data="app_post:all")]
    ]
    for v in vacancies:
        buttons.append([InlineKeyboardButton(
            text=f"💼 {v.title}",
            callback_data=f"app_post:vac:{v.id}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:applications")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_vacancy_detail_keyboard(vacancy_id: int, active: bool):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔴 Yopish" if active else "🟢 Ochish",
            callback_data=f"admin_vacancy_toggle:{vacancy_id}"
        )],
        [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"admin_vacancy_edit:{vacancy_id}")],
        [InlineKeyboardButton(text="📝 Savollar (saralash)", callback_data=f"vq:menu:{vacancy_id}")],
        [InlineKeyboardButton(text="📣 Foydalanuvchilarga e'lon", callback_data=f"vann:menu:{vacancy_id}")],
        [InlineKeyboardButton(text="📁 Arizalar", callback_data=f"admin_apps:{vacancy_id}")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"admin_vacancy_delete:{vacancy_id}")],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:vacancies")]
    ])


def announce_menu_keyboard(vacancy_id: int):
    """Vakansiyani foydalanuvchilarga e'lon qilish — auditoriya tanlash."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Barcha start bosganlar", callback_data=f"vann:all:{vacancy_id}")],
        [InlineKeyboardButton(text="🎯 Vakansiyaga ariza berganlar", callback_data=f"vann:pick:{vacancy_id}")],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data=f"admin_vacancy:{vacancy_id}")],
    ])


def announce_confirm_all_keyboard(vacancy_id: int, count: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ Ha, {count} kishiga yuborish", callback_data=f"vann:doall:{vacancy_id}")],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data=f"vann:menu:{vacancy_id}")],
    ])


def announce_pick_keyboard(vacancy_id: int, vacancies, picked: set):
    """Filtr uchun vakansiyalarni ko'p tanlash klaviaturasi."""
    buttons = []
    for v in vacancies:
        mark = "☑️" if v.id in picked else "⬜️"
        buttons.append([InlineKeyboardButton(
            text=f"{mark} {v.title}",
            callback_data=f"vann:tog:{vacancy_id}:{v.id}"
        )])
    buttons.append([InlineKeyboardButton(text="📤 Tanlanganlarga yuborish", callback_data=f"vann:send:{vacancy_id}")])
    buttons.append([InlineKeyboardButton(text="◀️ Ortga", callback_data=f"vann:menu:{vacancy_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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


# ── Saralash: vakansiya savollari (admin) ──────────────────────────────────

def vacancy_questions_menu_keyboard(vacancy_id: int, has_questions: bool):
    rows = [
        [InlineKeyboardButton(text="📋 Shablondan yuklash", callback_data=f"vq:tmpl:{vacancy_id}")],
    ]
    if has_questions:
        rows.append([InlineKeyboardButton(text="🗑 Savollarni o'chirish", callback_data=f"vq:clear:{vacancy_id}")])
    rows.append([InlineKeyboardButton(text="◀️ Ortga", callback_data=f"admin_vacancy:{vacancy_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def question_templates_keyboard(vacancy_id: int):
    from app.question_bank import QUESTION_BANK
    rows = [
        [InlineKeyboardButton(text=v["title"], callback_data=f"vq:set:{vacancy_id}:{key}")]
        for key, v in QUESTION_BANK.items()
    ]
    rows.append([InlineKeyboardButton(text="◀️ Ortga", callback_data=f"vq:menu:{vacancy_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Saralash: HR panel (reyting, baholash) ─────────────────────────────────

def screening_vacancies_keyboard(rows_data):
    """rows_data: [(vacancy, count), ...]"""
    rows = [
        [InlineKeyboardButton(text=f"💼 {v.title} — {cnt} nomzod", callback_data=f"scr:vac:{v.id}")]
        for v, cnt in rows_data
    ]
    rows.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def candidate_list_keyboard(apps, vacancy_id: int):
    from app.question_bank import color_for
    status_icon = {"submitted": "🕐", "approved": "✅", "rejected": "❌"}
    rows = []
    for a in apps:
        total = a.total_score
        score_txt = f"{total}/19" if total is not None else "baholanmagan"
        icon = color_for(total) if total is not None else "⚪️"
        st = status_icon.get(a.status, "")
        rows.append([InlineKeyboardButton(
            text=f"{icon}{st} {a.full_name or a.user_id} — {score_txt}",
            callback_data=f"scr:app:{a.id}"
        )])
    rows.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="scr:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def candidate_card_keyboard(app, written_answers, has_video: bool):
    rows = []
    for idx, ans in enumerate(written_answers, start=1):
        mark = f"({ans.score}/3)" if ans.score is not None else "baholash"
        rows.append([InlineKeyboardButton(
            text=f"✍️ Yozma {idx}: {mark}",
            callback_data=f"scr:wgrade:{app.id}:{ans.id}"
        )])
    if has_video:
        rows.append([InlineKeyboardButton(text="🎥 Videoni ko'rish", callback_data=f"scr:video:{app.id}")])
    vmark = f"({app.video_score}/4)" if app.video_score is not None else "baholash"
    rows.append([InlineKeyboardButton(text=f"🎬 Video ball: {vmark}", callback_data=f"scr:vgrade:{app.id}")])
    if app.status == "submitted":
        rows.append([
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"scr:approve:{app.id}"),
            InlineKeyboardButton(text="❌ Rad etish",  callback_data=f"scr:reject:{app.id}"),
        ])
    rows.append([InlineKeyboardButton(text="◀️ Ortga", callback_data=f"scr:vac:{app.vacancy_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def grade_written_keyboard(app_id: int, answer_id: int):
    btns = [InlineKeyboardButton(text=str(s), callback_data=f"scr:wset:{app_id}:{answer_id}:{s}") for s in range(4)]
    return InlineKeyboardMarkup(inline_keyboard=[
        btns,
        [InlineKeyboardButton(text="◀️ Ortga", callback_data=f"scr:app:{app_id}")],
    ])


def grade_video_keyboard(app_id: int):
    btns = [InlineKeyboardButton(text=str(s), callback_data=f"scr:vset:{app_id}:{s}") for s in range(5)]
    return InlineKeyboardMarkup(inline_keyboard=[
        btns,
        [InlineKeyboardButton(text="◀️ Ortga", callback_data=f"scr:app:{app_id}")],
    ])


def broadcast_segment_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Barcha foydalanuvchilar", callback_data="broadcast_seg:all")],
        [InlineKeyboardButton(text="👤 Faqat mijozlar", callback_data="broadcast_seg:client")],
        [InlineKeyboardButton(text="👷 Faqat ish izlovchilar", callback_data="broadcast_seg:jobseeker")],
    ])
