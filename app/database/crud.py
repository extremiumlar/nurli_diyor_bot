import json
from sqlalchemy import select, update, delete as sql_delete, func
from sqlalchemy.orm import selectinload
from app.database.connect import async_session
from app.database.models import (
    User, Project, ProjectStage, Subscription,
    Lead, Vacancy, Application, Admin, BotSettings,
    VacancyQuestion, ApplicationAnswer,
)


# ── Users ──────────────────────────────────────────────────────────────────

async def get_user(user_id: int):
    async with async_session() as session:
        return await session.get(User, user_id)


async def create_or_update_user(user_id: int, username: str | None, full_name: str | None):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.username = username
            user.full_name = full_name
        else:
            user = User(id=user_id, username=username, full_name=full_name)
            session.add(user)
        await session.commit()
        return user


async def update_user_role(user_id: int, role: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.role = role
            await session.commit()


async def update_user_phone(user_id: int, phone: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.phone = phone
            await session.commit()


async def get_all_subscribed_users():
    async with async_session() as session:
        result = await session.execute(select(User).where(User.is_subscribed == True))
        return result.scalars().all()


async def get_users_by_role(role: str):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.role == role, User.is_subscribed == True)
        )
        return result.scalars().all()


async def get_applicant_ids_by_vacancies(vacancy_ids: list[int]) -> set[int]:
    """Berilgan vakansiyalarga ariza topshirgan foydalanuvchilarning ID lari (unikal)."""
    if not vacancy_ids:
        return set()
    async with async_session() as session:
        result = await session.execute(
            select(Application.user_id).where(Application.vacancy_id.in_(vacancy_ids))
        )
        return set(result.scalars().all())


async def set_user_unsubscribed(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.is_subscribed = False
            await session.commit()


# ── Projects ───────────────────────────────────────────────────────────────

async def get_active_projects():
    async with async_session() as session:
        result = await session.execute(
            select(Project).where(Project.active == True)
        )
        return result.scalars().all()


async def get_project(project_id: int):
    async with async_session() as session:
        return await session.get(Project, project_id)


async def get_all_projects():
    async with async_session() as session:
        result = await session.execute(select(Project))
        return result.scalars().all()


async def create_project(name: str, address: str, description: str):
    async with async_session() as session:
        project = Project(name=name, address=address, description=description)
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project


async def update_project(project_id: int, **kwargs):
    async with async_session() as session:
        project = await session.get(Project, project_id)
        if project:
            for key, value in kwargs.items():
                setattr(project, key, value)
            await session.commit()


async def archive_project(project_id: int):
    async with async_session() as session:
        project = await session.get(Project, project_id)
        if project:
            project.active = False
            await session.commit()


# ── Project Stages ─────────────────────────────────────────────────────────

async def get_project_stages(project_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(ProjectStage)
            .where(ProjectStage.project_id == project_id)
            .order_by(ProjectStage.order_num)
        )
        return result.scalars().all()


async def get_stage(stage_id: int):
    async with async_session() as session:
        return await session.get(ProjectStage, stage_id)


async def create_stage(project_id: int, name: str, order_num: int):
    async with async_session() as session:
        stage = ProjectStage(project_id=project_id, name=name, order_num=order_num)
        session.add(stage)
        await session.commit()
        await session.refresh(stage)
        return stage


async def update_stage(stage_id: int, **kwargs):
    from datetime import datetime
    async with async_session() as session:
        stage = await session.get(ProjectStage, stage_id)
        if stage:
            for key, value in kwargs.items():
                setattr(stage, key, value)
            stage.updated_at = datetime.now()
            await session.commit()


# ── Subscriptions ──────────────────────────────────────────────────────────

async def subscribe_user(user_id: int, project_id: int):
    async with async_session() as session:
        sub = await session.get(Subscription, (user_id, project_id))
        if sub:
            sub.active = True
        else:
            sub = Subscription(user_id=user_id, project_id=project_id)
            session.add(sub)
        await session.commit()


async def unsubscribe_user(user_id: int, project_id: int):
    async with async_session() as session:
        sub = await session.get(Subscription, (user_id, project_id))
        if sub:
            sub.active = False
            await session.commit()


async def get_project_subscribers(project_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Subscription)
            .where(Subscription.project_id == project_id, Subscription.active == True)
        )
        return result.scalars().all()


async def get_user_subscriptions(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id, Subscription.active == True)
        )
        return result.scalars().all()


# ── Leads ──────────────────────────────────────────────────────────────────

async def create_lead(user_id: int, full_name: str, phone: str, project_id: int | None, note: str | None):
    async with async_session() as session:
        lead = Lead(
            user_id=user_id,
            full_name=full_name,
            phone=phone,
            project_id=project_id,
            note=note
        )
        session.add(lead)
        await session.commit()
        await session.refresh(lead)
        return lead


async def get_all_leads(project_id: int | None = None):
    async with async_session() as session:
        q = select(Lead)
        if project_id:
            q = q.where(Lead.project_id == project_id)
        result = await session.execute(q.order_by(Lead.created_at.desc()))
        return result.scalars().all()


# ── Vacancies ──────────────────────────────────────────────────────────────

async def get_active_vacancies():
    async with async_session() as session:
        result = await session.execute(
            select(Vacancy).where(Vacancy.active == True)
        )
        return result.scalars().all()


async def get_vacancy(vacancy_id: int):
    async with async_session() as session:
        return await session.get(Vacancy, vacancy_id)


async def get_all_vacancies():
    async with async_session() as session:
        result = await session.execute(select(Vacancy))
        return result.scalars().all()


async def create_vacancy(title: str, requirements: str, salary: str | None = None):
    async with async_session() as session:
        v = Vacancy(title=title, requirements=requirements, salary=salary)
        session.add(v)
        await session.commit()
        await session.refresh(v)
        return v


async def update_vacancy(vacancy_id: int, **kwargs):
    async with async_session() as session:
        v = await session.get(Vacancy, vacancy_id)
        if v:
            for key, value in kwargs.items():
                setattr(v, key, value)
            await session.commit()
            await session.refresh(v)
        return v


async def bulk_update_vacancies(vacancy_ids: list[int], **fields) -> int:
    """Bir nechta vakansiyaning sozlamasini birdan o'zgartiradi.
    O'zgartirilgan vakansiyalar sonini qaytaradi."""
    if not vacancy_ids or not fields:
        return 0
    async with async_session() as session:
        result = await session.execute(
            update(Vacancy).where(Vacancy.id.in_(vacancy_ids)).values(**fields)
        )
        await session.commit()
        return result.rowcount or 0


async def toggle_vacancy(vacancy_id: int, active: bool):
    async with async_session() as session:
        v = await session.get(Vacancy, vacancy_id)
        if v:
            v.active = active
            await session.commit()


async def delete_vacancy(vacancy_id: int):
    """Vacancy va unga bog'liq arizalarni o'chiradi."""
    async with async_session() as session:
        # avval arizalarni o'chirish (FK constraint)
        from sqlalchemy import delete as sql_delete
        await session.execute(
            sql_delete(Application).where(Application.vacancy_id == vacancy_id)
        )
        v = await session.get(Vacancy, vacancy_id)
        if v:
            await session.delete(v)
        await session.commit()


# ── Applications ───────────────────────────────────────────────────────────

async def create_application(user_id: int, full_name: str, phone: str,
                              address: str | None, age: int | None,
                              languages: str | None, education: str | None,
                              vacancy_id: int, experience: str | None,
                              additional_skills: str | None,
                              photo_file_id: str | None = None,
                              cv_file_id: str | None = None):
    async with async_session() as session:
        app = Application(
            user_id=user_id,
            full_name=full_name,
            phone=phone,
            address=address,
            age=age,
            languages=languages,
            education=education,
            vacancy_id=vacancy_id,
            experience=experience,
            additional_skills=additional_skills,
            photo_file_id=photo_file_id,
            cv_file_id=cv_file_id
        )
        session.add(app)
        await session.commit()
        await session.refresh(app)
        return app


async def has_applied_today(user_id: int, vacancy_id: int) -> bool:
    """Bugun shu vakansiyaga TUGATILGAN ariza topshirilganmi.

    Tugatilmagan (in_progress) arizalar hisobga olinmaydi — aks holda
    nomzod oqimni yarmida tashlab ketsa, shu kuni qayta topshira olmay qoladi.
    """
    from datetime import date
    from sqlalchemy import func
    async with async_session() as session:
        today = date.today().isoformat()
        result = await session.execute(
            select(Application).where(
                Application.user_id == user_id,
                Application.vacancy_id == vacancy_id,
                Application.status != "in_progress",
                func.date(Application.created_at) == today
            )
        )
        return result.scalars().first() is not None


async def get_applications(vacancy_id: int | None = None):
    async with async_session() as session:
        q = select(Application)
        if vacancy_id:
            q = q.where(Application.vacancy_id == vacancy_id)
        result = await session.execute(q.order_by(Application.created_at.desc()))
        return result.scalars().all()


async def get_application(app_id: int):
    async with async_session() as session:
        return await session.get(Application, app_id)


async def delete_application(app_id: int):
    async with async_session() as session:
        app = await session.get(Application, app_id)
        if app:
            await session.delete(app)
            await session.commit()
            return True
        return False


# ── Admins ─────────────────────────────────────────────────────────────────

async def get_admin(telegram_id: int):
    async with async_session() as session:
        admin = await session.get(Admin, telegram_id)
        if admin and admin.active:
            return admin
        return None


async def add_admin(telegram_id: int, full_name: str, role: str, added_by: int):
    async with async_session() as session:
        existing = await session.get(Admin, telegram_id)
        if existing:
            existing.active = True
            existing.role = role
        else:
            admin = Admin(
                telegram_id=telegram_id,
                full_name=full_name,
                role=role,
                added_by=added_by
            )
            session.add(admin)
        await session.commit()


async def remove_admin(telegram_id: int):
    async with async_session() as session:
        admin = await session.get(Admin, telegram_id)
        if admin:
            admin.active = False
            await session.commit()


async def get_all_admins():
    async with async_session() as session:
        result = await session.execute(
            select(Admin).where(Admin.active == True)
        )
        return result.scalars().all()


async def get_admins_by_role(role: str):
    async with async_session() as session:
        result = await session.execute(
            select(Admin).where(Admin.role == role, Admin.active == True)
        )
        return result.scalars().all()


async def update_admin_role(telegram_id: int, new_role: str):
    async with async_session() as session:
        admin = await session.get(Admin, telegram_id)
        if admin:
            admin.role = new_role
            await session.commit()


# ── Bot sozlamalari ────────────────────────────────────────────────────────

async def get_setting(key: str) -> str | None:
    async with async_session() as session:
        obj = await session.get(BotSettings, key)
        return obj.value if obj else None


async def set_setting(key: str, value: str | None):
    async with async_session() as session:
        obj = await session.get(BotSettings, key)
        if obj:
            obj.value = value
        else:
            obj = BotSettings(key=key, value=value)
            session.add(obj)
        await session.commit()


# ── Vakansiya savollari (saralash) ─────────────────────────────────────────

async def get_vacancy_questions(vacancy_id: int, qtype: str | None = None):
    async with async_session() as session:
        q = select(VacancyQuestion).where(VacancyQuestion.vacancy_id == vacancy_id)
        if qtype:
            q = q.where(VacancyQuestion.qtype == qtype)
        q = q.order_by(VacancyQuestion.qtype, VacancyQuestion.order_num)
        result = await session.execute(q)
        return result.scalars().all()


async def count_vacancy_questions(vacancy_id: int) -> int:
    async with async_session() as session:
        result = await session.execute(
            select(func.count()).select_from(VacancyQuestion)
            .where(VacancyQuestion.vacancy_id == vacancy_id)
        )
        return result.scalar() or 0


async def delete_vacancy_questions(vacancy_id: int):
    async with async_session() as session:
        await session.execute(
            sql_delete(VacancyQuestion).where(VacancyQuestion.vacancy_id == vacancy_id)
        )
        await session.commit()


async def save_question_set(vacancy_id: int, data: dict) -> int:
    """Savol to'plamini (AI yaratgan yoki bankdan) vakansiyaga saqlaydi.

    data: {"test": [{"text","options":[{"text","score"}]}],
           "written": [{"text","rubric"}], "video": "..."}
    Eski savollar almashtiriladi. Qo'shilgan savollar sonini qaytaradi.
    """
    from app.question_bank import VIDEO_RUBRIC
    async with async_session() as session:
        await session.execute(
            sql_delete(VacancyQuestion).where(VacancyQuestion.vacancy_id == vacancy_id)
        )
        added = 0
        for i, t in enumerate(data.get("test", []), start=1):
            session.add(VacancyQuestion(
                vacancy_id=vacancy_id, qtype="test", order_num=i,
                text=t["text"], options=json.dumps(t["options"], ensure_ascii=False),
            ))
            added += 1
        for i, w in enumerate(data.get("written", []), start=1):
            session.add(VacancyQuestion(
                vacancy_id=vacancy_id, qtype="written", order_num=i,
                text=w["text"], rubric=w.get("rubric"),
            ))
            added += 1
        if data.get("video"):
            session.add(VacancyQuestion(
                vacancy_id=vacancy_id, qtype="video", order_num=1,
                text=data["video"], rubric=VIDEO_RUBRIC,
            ))
            added += 1
        await session.commit()
        return added


async def get_question(question_id: int):
    async with async_session() as session:
        return await session.get(VacancyQuestion, question_id)


async def update_question_text(question_id: int, text: str):
    async with async_session() as session:
        q = await session.get(VacancyQuestion, question_id)
        if q:
            q.text = text
            await session.commit()
        return q


async def update_question_option(question_id: int, pos: int, text: str):
    """Test savolining bitta variant matnini o'zgartiradi (ball o'zgarmaydi)."""
    async with async_session() as session:
        q = await session.get(VacancyQuestion, question_id)
        if not q or not q.options:
            return None
        opts = json.loads(q.options)
        if not (0 <= pos < len(opts)):
            return None
        opts[pos]["text"] = text
        q.options = json.dumps(opts, ensure_ascii=False)
        await session.commit()
        return q


async def delete_question(question_id: int):
    """Bitta savolni o'chiradi va qolganlarining tartibini tiklaydi."""
    async with async_session() as session:
        q = await session.get(VacancyQuestion, question_id)
        if not q:
            return False
        vid, qtype = q.vacancy_id, q.qtype
        await session.delete(q)
        await session.commit()
        result = await session.execute(
            select(VacancyQuestion)
            .where(VacancyQuestion.vacancy_id == vid, VacancyQuestion.qtype == qtype)
            .order_by(VacancyQuestion.order_num)
        )
        for i, item in enumerate(result.scalars().all(), start=1):
            item.order_num = i
        await session.commit()
        return True


async def add_question(vacancy_id: int, qtype: str, text: str,
                       options: list | None = None, rubric: str | None = None):
    """Vakansiyaga yangi savol qo'shadi (oxiriga)."""
    async with async_session() as session:
        result = await session.execute(
            select(func.max(VacancyQuestion.order_num)).where(
                VacancyQuestion.vacancy_id == vacancy_id,
                VacancyQuestion.qtype == qtype,
            )
        )
        nxt = (result.scalar() or 0) + 1
        q = VacancyQuestion(
            vacancy_id=vacancy_id, qtype=qtype, order_num=nxt, text=text,
            options=json.dumps(options, ensure_ascii=False) if options else None,
            rubric=rubric,
        )
        session.add(q)
        await session.commit()
        await session.refresh(q)
        return q


async def set_questions_from_bank(vacancy_id: int, bank_key: str) -> int:
    """QUESTION_BANK'dagi shablonni vakansiyaga nusxalaydi (eskilarini o'chirib).
    Qo'shilgan savollar sonini qaytaradi."""
    from app.question_bank import QUESTION_BANK
    tmpl = QUESTION_BANK.get(bank_key)
    if not tmpl:
        return 0
    async with async_session() as session:
        await session.execute(
            sql_delete(VacancyQuestion).where(VacancyQuestion.vacancy_id == vacancy_id)
        )
        added = 0
        for i, t in enumerate(tmpl.get("test", []), start=1):
            session.add(VacancyQuestion(
                vacancy_id=vacancy_id, qtype="test", order_num=i,
                text=t["text"], options=json.dumps(t["options"], ensure_ascii=False),
            ))
            added += 1
        for i, w in enumerate(tmpl.get("written", []), start=1):
            session.add(VacancyQuestion(
                vacancy_id=vacancy_id, qtype="written", order_num=i,
                text=w["text"], rubric=w.get("rubric"),
            ))
            added += 1
        # 3-bosqich: rolga xos majburiy video-savol
        if tmpl.get("video"):
            from app.question_bank import VIDEO_RUBRIC
            session.add(VacancyQuestion(
                vacancy_id=vacancy_id, qtype="video", order_num=1,
                text=tmpl["video"], rubric=VIDEO_RUBRIC,
            ))
            added += 1
        await session.commit()
        return added


# ── Nomzod javoblari va saralash ───────────────────────────────────────────

async def create_answer(application_id: int, question_id: int | None, qtype: str,
                        order_num: int, question_text: str | None,
                        answer_text: str | None, score: int | None,
                        max_score: int | None):
    """Javob yozadi — dublikatga chidamli (idempotent).

    (application_id, question_id) juftligi allaqachon bo'lsa — jim o'tadi
    (uq_answer_app_question indeksi, tahlil/C2.md R1). Shu tufayli takror
    bosish, webhook retry yoki ikki worker poygasi ikkinchi qator yozolmaydi.
    question_id NULL bo'lsa cheklov qo'llanmaydi (oddiy INSERT).
    """
    values = dict(
        application_id=application_id, question_id=question_id, qtype=qtype,
        order_num=order_num, question_text=question_text, answer_text=answer_text,
        score=score, max_score=max_score,
    )
    async with async_session() as session:
        dialect = session.bind.dialect.name
        if dialect in ("sqlite", "postgresql"):
            if dialect == "sqlite":
                from sqlalchemy.dialects.sqlite import insert as _insert
            else:
                from sqlalchemy.dialects.postgresql import insert as _insert
            # Maqsadsiz ON CONFLICT DO NOTHING: indeks hali qurilmagan
            # bazada ham xato bermaydi (shunchaki eski xatti-harakat qoladi).
            stmt = _insert(ApplicationAnswer).values(**values).on_conflict_do_nothing()
            await session.execute(stmt)
        else:
            session.add(ApplicationAnswer(**values))
        await session.commit()


async def get_application_answers(application_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(ApplicationAnswer)
            .where(ApplicationAnswer.application_id == application_id)
            .order_by(ApplicationAnswer.qtype, ApplicationAnswer.order_num)
        )
        return result.scalars().all()


async def update_application(app_id: int, **kwargs):
    async with async_session() as session:
        app = await session.get(Application, app_id)
        if app:
            for key, value in kwargs.items():
                setattr(app, key, value)
            await session.commit()
            await session.refresh(app)
        return app


async def update_answer_score(answer_id: int, score: int | None):
    async with async_session() as session:
        a = await session.get(ApplicationAnswer, answer_id)
        if a:
            a.score = score
            await session.commit()


async def set_answer_ai_feedback(answer_id: int, feedback: str | None):
    """AI baholash izohini saqlaydi (HR ko'radi)."""
    async with async_session() as session:
        a = await session.get(ApplicationAnswer, answer_id)
        if a:
            a.ai_feedback = feedback
            await session.commit()


async def recompute_scores(app_id: int):
    """Ariza ballarini javoblardan qayta hisoblaydi.

    Jami ball faqat QO'LLANILADIGAN bosqichlar to'liq baholanganda chiqadi.
    Masalan video o'chirilgan vakansiyada video bali kutilmaydi.
    """
    async with async_session() as session:
        app = await session.get(Application, app_id)
        if not app:
            return None
        result = await session.execute(
            select(ApplicationAnswer).where(ApplicationAnswer.application_id == app_id)
        )
        answers = result.scalars().all()
        tests   = [a for a in answers if a.qtype == "test"]
        written = [a for a in answers if a.qtype == "written"]

        if tests:
            app.test_score = sum((a.score or 0) for a in tests)
        if written and all(a.score is not None for a in written):
            app.written_score = sum(a.score for a in written)

        # Chegara-signal: ball maksimumdan oshsa — dublikat javob belgisi
        # (uq_answer_app_question buni to'sishi kerak; bu log — lakmus qog'oz)
        from app.question_bank import MAX_TEST, MAX_WRITTEN
        if (app.test_score or 0) > MAX_TEST or (app.written_score or 0) > MAX_WRITTEN:
            print(f"[SCORE WARNING] Ariza #{app.id}: test={app.test_score}/"
                  f"{MAX_TEST} yozma={app.written_score}/{MAX_WRITTEN} — "
                  f"chegaradan yuqori, dublikat javob bo'lishi mumkin!",
                  flush=True)

        # Qaysi bosqichlar shu arizaga tegishli — vakansiya sozlamasidan
        from app.question_bank import STAGE_ON
        vac = await session.get(Vacancy, app.vacancy_id) if app.vacancy_id else None
        q_mode = "required" if vac is None else (vac.questions_mode or "required")
        v_mode = "required" if vac is None else (vac.video_mode or "required")
        q_on = q_mode in STAGE_ON

        parts, ready = 0, True
        if q_on:
            if app.test_score is None or app.written_score is None:
                ready = False
            else:
                parts += app.test_score + app.written_score
        if v_mode in STAGE_ON:
            if app.video_score is None:
                ready = False
            else:
                parts += app.video_score

        app.total_score = parts if ready else None
        await session.commit()
        await session.refresh(app)
        return app
