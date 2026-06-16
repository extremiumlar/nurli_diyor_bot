from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.database.connect import async_session
from app.database.models import (
    User, Project, ProjectStage, Subscription,
    Lead, Vacancy, Application, Admin
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


async def create_vacancy(title: str, requirements: str, schedule: str, salary: str | None = None):
    async with async_session() as session:
        v = Vacancy(title=title, requirements=requirements, schedule=schedule, salary=salary)
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
                              additional_skills: str | None, cv_file_id: str):
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
            cv_file_id=cv_file_id
        )
        session.add(app)
        await session.commit()
        await session.refresh(app)
        return app


async def has_applied_today(user_id: int, vacancy_id: int) -> bool:
    from datetime import date
    from sqlalchemy import func
    async with async_session() as session:
        today = date.today().isoformat()
        result = await session.execute(
            select(Application).where(
                Application.user_id == user_id,
                Application.vacancy_id == vacancy_id,
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
