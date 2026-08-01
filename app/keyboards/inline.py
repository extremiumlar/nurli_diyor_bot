from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Telegram tugma matni uzun bo'lsa kesib tashlaydi va tugma sig'may qoladi.
# Dinamik matnlarni (vakansiya nomi, nomzod ismi) shu chegara bilan qisqartiramiz.
BTN_MAX = 28


def cut(text: str, limit: int = BTN_MAX) -> str:
    """Tugma matnini xavfsiz uzunlikka qisqartiradi."""
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def subscribe_keyboard(channel_link: str, instagram_url: str | None) -> InlineKeyboardMarkup:
    """Majburiy obuna tugmalari. Instagram URL yo'q bo'lsa — faqat kanal ko'rsatiladi."""
    social_row = [InlineKeyboardButton(text="📢 Telegram kanal", url=channel_link)]
    if instagram_url:
        social_row.append(InlineKeyboardButton(text="📸 Instagram", url=instagram_url))
    return InlineKeyboardMarkup(inline_keyboard=[
        social_row,
        [InlineKeyboardButton(text="✅ Tekshirish",
                              callback_data="check_subscribe")],
    ])


def not_subscribed_keyboard(channel_link: str, instagram_url: str | None) -> InlineKeyboardMarkup:
    """Faqat Telegram ga obuna bo'lmagan holatda."""
    rows = [[InlineKeyboardButton(text="📢 Telegram kanal", url=channel_link)]]
    if instagram_url:
        rows.append([InlineKeyboardButton(text="📸 Instagram", url=instagram_url)])
    rows.append([InlineKeyboardButton(text="✅ Tekshirish",
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
        InlineKeyboardButton(text="⏭️ O'tkazish", callback_data="skip")
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
        buttons.append([InlineKeyboardButton(text="👥 Adminlar", callback_data="admin:admins")])
    # Sozlamalar HR uchun ham ochiq (kanal, guruh, Instagram)
    if role in ("super_admin", "hr_admin"):
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
        [InlineKeyboardButton(text="📸 Bosqich foto", callback_data=f"admin_stage_photo:{project_id}")],
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
            text=cut(f"{'🟢' if v.active else '🔴'} {v.title}"),
            callback_data=f"admin_vacancy:{v.id}"
        )]
        for v in vacancies
    ]
    buttons.append([InlineKeyboardButton(text="➕ Yangi vakansiya", callback_data="admin_vacancy:new")])
    buttons.append([InlineKeyboardButton(text="🤖 Savollarni biriktirish", callback_data="vq:autoall")])
    buttons.append([InlineKeyboardButton(text="🔄 Savollarni yangilash", callback_data="vq:autoall:force")])
    buttons.append([InlineKeyboardButton(text="📢 Guruhga yuborish", callback_data="vac_post:menu")])
    buttons.append([InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def vacancy_post_menu_keyboard(vacancies):
    """Guruhga yuborish menyusi: Barcha faollar yoki bittasini tanlash."""
    buttons = [
        [InlineKeyboardButton(text="📁 Barchasi", callback_data="vac_post:all")]
    ]
    for v in vacancies:
        if not v.active:
            continue
        buttons.append([InlineKeyboardButton(
            text=cut(f"💼 {v.title}"),
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
            text=cut(f"💼 {v.title}"),
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
        [InlineKeyboardButton(text="📝 Savollar", callback_data=f"vq:menu:{vacancy_id}")],
        [InlineKeyboardButton(text="📣 E'lon qilish", callback_data=f"vann:menu:{vacancy_id}")],
        [InlineKeyboardButton(text="📁 Arizalar", callback_data=f"admin_apps:{vacancy_id}")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"admin_vacancy_delete:{vacancy_id}")],
        [InlineKeyboardButton(text="◀️ Ortga", callback_data="admin:vacancies")]
    ])


def announce_menu_keyboard(vacancy_id: int):
    """Vakansiyani foydalanuvchilarga e'lon qilish — auditoriya tanlash."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Hammaga", callback_data=f"vann:all:{vacancy_id}")],
        [InlineKeyboardButton(text="🎯 Ariza berganlarga", callback_data=f"vann:pick:{vacancy_id}")],
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
            text=cut(f"{mark} {v.title}"),
            callback_data=f"vann:tog:{vacancy_id}:{v.id}"
        )])
    buttons.append([InlineKeyboardButton(text="📤 Yuborish", callback_data=f"vann:send:{vacancy_id}")])
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
            text=cut(f"{ROLE_LABELS.get(a.role, a.role)} | {a.full_name or a.telegram_id}"),
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

def vacancy_questions_menu_keyboard(vacancy_id: int, has_questions: bool,
                                    ai_available: bool = False):
    rows = []
    if ai_available:
        rows.append([InlineKeyboardButton(text="🤖 AI bilan yaratish",
                                          callback_data=f"vq:ai:{vacancy_id}")])
    rows.append([InlineKeyboardButton(text="📋 Shablondan yuklash",
                                      callback_data=f"vq:tmpl:{vacancy_id}")])
    if has_questions:
        rows.append([InlineKeyboardButton(text="✏️ Savollarni tahrirlash",
                                          callback_data=f"vq:edit:{vacancy_id}")])
        rows.append([InlineKeyboardButton(text="🗑 Savollarni o'chirish",
                                          callback_data=f"vq:clear:{vacancy_id}")])
    else:
        rows.append([InlineKeyboardButton(text="✍️ Qo'lda yaratish",
                                          callback_data=f"vq:edit:{vacancy_id}")])
    rows.append([InlineKeyboardButton(text="◀️ Ortga", callback_data=f"admin_vacancy:{vacancy_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def ai_questions_review_keyboard(vacancy_id: int):
    """AI yaratgan to'plamni tasdiqlash."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Saqlash", callback_data=f"vq:aisave:{vacancy_id}")],
        [InlineKeyboardButton(text="🔄 Qayta yaratish", callback_data=f"vq:ai:{vacancy_id}")],
        [InlineKeyboardButton(text="◀️ Bekor", callback_data=f"vq:menu:{vacancy_id}")],
    ])


QTYPE_LABEL = {"test": "🧠", "written": "✍️", "video": "🎥"}


def questions_list_keyboard(vacancy_id: int, questions):
    """Savollar ro'yxati — tahrirlash uchun."""
    rows = []
    counters = {}
    for q in questions:
        n = counters.get(q.qtype, 0) + 1
        counters[q.qtype] = n
        icon = QTYPE_LABEL.get(q.qtype, "•")
        label = f"{icon} {n}. {q.text}"
        rows.append([InlineKeyboardButton(text=cut(label, 34),
                                          callback_data=f"vq:q:{q.id}")])
    rows.append([
        InlineKeyboardButton(text="➕ Test", callback_data=f"vq:add:test:{vacancy_id}"),
        InlineKeyboardButton(text="➕ Yozma", callback_data=f"vq:add:written:{vacancy_id}"),
    ])
    rows.append([InlineKeyboardButton(text="🎥 Video-savol",
                                      callback_data=f"vq:add:video:{vacancy_id}")])
    rows.append([InlineKeyboardButton(text="◀️ Ortga", callback_data=f"vq:menu:{vacancy_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def question_detail_keyboard(q, n_options: int = 0):
    """Bitta savol ustidagi amallar."""
    rows = [[InlineKeyboardButton(text="✏️ Savol matni", callback_data=f"vq:qtext:{q.id}")]]
    if q.qtype == "test" and n_options:
        letters = ["A", "B", "C", "D", "E"]
        row = [InlineKeyboardButton(text=f"✏️ {letters[i]}",
                                    callback_data=f"vq:opt:{q.id}:{i}")
               for i in range(min(n_options, 5))]
        rows.append(row)
    rows.append([InlineKeyboardButton(text="🗑 Savolni o'chirish",
                                      callback_data=f"vq:qdel:{q.id}")])
    rows.append([InlineKeyboardButton(text="◀️ Ortga",
                                      callback_data=f"vq:edit:{q.vacancy_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def question_templates_keyboard(vacancy_id: int):
    from app.question_bank import QUESTION_BANK
    rows = [
        [InlineKeyboardButton(text=cut(v["title"]), callback_data=f"vq:set:{vacancy_id}:{key}")]
        for key, v in QUESTION_BANK.items()
    ]
    rows.append([InlineKeyboardButton(text="◀️ Ortga", callback_data=f"vq:menu:{vacancy_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ── Nomzod kartochkasi ustidagi harakat tugmalari ─────────────────────────
# MUHIM: tugma matnlari QISQA bo'lishi shart — Telegram uzun matnni kesib
# tashlaydi va tugmalar bir qatorga sig'may qoladi.

def _view_rows(app):
    """Ko'rish tugmalari — ikkala holatda ham bir xil."""
    rows = []
    if app.video_file_id:
        rows.append([InlineKeyboardButton(text="🎥 Video", callback_data=f"cd:video:{app.id}")])
    rows.append([
        InlineKeyboardButton(text="🧠 Test",  callback_data=f"cd:tests:{app.id}"),
        InlineKeyboardButton(text="✍️ Yozma", callback_data=f"cd:written:{app.id}"),
    ])
    if getattr(app, "ai_summary", None):
        rows.append([InlineKeyboardButton(text="🤖 AI xulosasi", callback_data=f"cd:ai:{app.id}")])
    return rows


def candidate_actions_keyboard(app):
    """HR/guruhga yuborilgan nomzod xabari ostidagi tugmalar."""
    rows = _view_rows(app)
    rows.append([InlineKeyboardButton(text="⭐️ Baholash", callback_data=f"cd:grade:{app.id}")])
    rows.append([
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"cd:ask_ok:{app.id}"),
        InlineKeyboardButton(text="❌ Rad etish",  callback_data=f"cd:ask_no:{app.id}"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def candidate_decided_keyboard(app):
    """Qaror qabul qilingandan keyingi tugmalar (ko'rish + qaytarish)."""
    rows = _view_rows(app)
    rows.append([InlineKeyboardButton(text="↩️ Qarorni qaytarish", callback_data=f"cd:undo:{app.id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_decision_keyboard(app_id: int, decision: str):
    """decision: 'ok' (tasdiqlash) yoki 'no' (rad etish) — tasdiq so'raladi."""
    yes_text = "✅ Ha, tasdiqlayman" if decision == "ok" else "❌ Ha, rad etaman"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=yes_text, callback_data=f"cd:do_{decision}:{app_id}")],
        [InlineKeyboardButton(text="◀️ Bekor", callback_data=f"cd:back:{app_id}")],
    ])


def grade_menu_keyboard(app, written_answers, ai_available: bool = False):
    """Baholash menyusi: yozma javoblar + video (+ AI qayta baholash)."""
    rows = []
    for idx, ans in enumerate(written_answers, start=1):
        mark = f"{ans.score}/3" if ans.score is not None else "—"
        ai = "🤖" if getattr(ans, "ai_feedback", None) else ""
        rows.append([InlineKeyboardButton(
            text=f"✍️ Yozma {idx}: {mark} {ai}".strip(),
            callback_data=f"cd:wgrade:{app.id}:{ans.id}"
        )])
    vmark = f"{app.video_score}/4" if app.video_score is not None else "—"
    rows.append([InlineKeyboardButton(text=f"🎬 Video: {vmark}", callback_data=f"cd:vgrade:{app.id}")])
    if ai_available:
        rows.append([InlineKeyboardButton(text="🤖 AI qayta baholash",
                                         callback_data=f"cd:regrade:{app.id}")])
    rows.append([InlineKeyboardButton(text="◀️ Ortga", callback_data=f"cd:back:{app.id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def grade_written_keyboard(app_id: int, answer_id: int):
    btns = [InlineKeyboardButton(text=str(s), callback_data=f"cd:wset:{app_id}:{answer_id}:{s}")
            for s in range(4)]
    return InlineKeyboardMarkup(inline_keyboard=[
        btns,
        [InlineKeyboardButton(text="◀️ Ortga", callback_data=f"cd:grade:{app_id}")],
    ])


def grade_video_keyboard(app_id: int):
    btns = [InlineKeyboardButton(text=str(s), callback_data=f"cd:vset:{app_id}:{s}")
            for s in range(5)]
    return InlineKeyboardMarkup(inline_keyboard=[
        btns,
        [InlineKeyboardButton(text="◀️ Ortga", callback_data=f"cd:grade:{app_id}")],
    ])


def broadcast_segment_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Barcha foydalanuvchilar", callback_data="broadcast_seg:all")],
        [InlineKeyboardButton(text="👤 Faqat mijozlar", callback_data="broadcast_seg:client")],
        [InlineKeyboardButton(text="👷 Faqat ish izlovchilar", callback_data="broadcast_seg:jobseeker")],
    ])
