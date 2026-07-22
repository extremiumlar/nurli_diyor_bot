from sqlalchemy import (
    BigInteger, String, Boolean, DateTime, Text,
    Integer, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connect import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    role: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128))
    address: Mapped[str | None] = mapped_column(String(256), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())

    stages: Mapped[list["ProjectStage"]] = relationship(back_populates="project")


class ProjectStage(Base):
    __tablename__ = "project_stages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    photo_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_num: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="stages")


class Subscription(Base):
    __tablename__ = "subscriptions"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), primary_key=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    project_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("projects.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128))
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    schedule: Mapped[str | None] = mapped_column(String(128), nullable=True)
    salary: Mapped[str | None] = mapped_column(String(128), nullable=True)
    salary_ceiling: Mapped[int | None] = mapped_column(Integer, nullable=True)  # byudjet shifti (💰 belgi uchun)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())


class VacancyQuestion(Base):
    """Vakansiya bo'yicha saralash savollari (2-bosqich)."""
    __tablename__ = "vacancy_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vacancy_id: Mapped[int] = mapped_column(Integer, ForeignKey("vacancies.id"))
    qtype: Mapped[str] = mapped_column(String(10))          # 'test' | 'written'
    order_num: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text)
    options: Mapped[str | None] = mapped_column(Text, nullable=True)  # test uchun JSON: [{"text","score"}]
    rubric: Mapped[str | None] = mapped_column(Text, nullable=True)   # yozma uchun AI/HR baholash mezoni


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(String(256), nullable=True)   # qayerdan
    birth_year: Mapped[str | None] = mapped_column(String(10), nullable=True) # legacy: tug'ilgan yili
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)            # yosh
    languages: Mapped[str | None] = mapped_column(String(256), nullable=True) # qaysi tillarni biladi
    education: Mapped[str | None] = mapped_column(String(128), nullable=True) # ma'lumoti
    vacancy_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vacancies.id"), nullable=True)
    experience: Mapped[str | None] = mapped_column(Text, nullable=True)        # qayerda ishlagan
    additional_skills: Mapped[str | None] = mapped_column(Text, nullable=True) # qo'shimcha bilim va ko'nikmalar
    photo_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True) # rasm
    cv_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())

    # ── Saralash tizimi (3-bosqich) ────────────────────────────────────────
    expected_salary: Mapped[str | None] = mapped_column(String(64), nullable=True)  # kutgan maosh
    stage: Mapped[str] = mapped_column(String(12), default="stage1")   # stage1|stage2|stage3|done
    status: Mapped[str] = mapped_column(String(12), default="in_progress")  # in_progress|submitted|approved|rejected
    test_score: Mapped[int | None] = mapped_column(Integer, nullable=True)      # 0–9
    written_score: Mapped[int | None] = mapped_column(Integer, nullable=True)   # 0–6
    video_score: Mapped[int | None] = mapped_column(Integer, nullable=True)     # 0–4
    total_score: Mapped[int | None] = mapped_column(Integer, nullable=True)     # 0–19
    video_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    video_is_note: Mapped[bool] = mapped_column(Boolean, default=False)         # video_note (dumaloq) yoki oddiy video
    hr_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reviewed_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)


class ApplicationAnswer(Base):
    """Nomzodning har bir savolga bergan javobi va bali."""
    __tablename__ = "application_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id"))
    question_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("vacancy_questions.id"), nullable=True)
    qtype: Mapped[str] = mapped_column(String(10))            # 'test' | 'written'
    order_num: Mapped[int] = mapped_column(Integer, default=0)
    question_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # snapshot (savol keyin o'zgarsa ham saqlanadi)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)    # tanlangan variant matni yoki yozma javob
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)    # keyinchalik AI izohi


class BotSettings(Base):
    __tablename__ = "bot_settings"

    key:   Mapped[str]      = mapped_column(String(64), primary_key=True)
    value: Mapped[str|None] = mapped_column(Text, nullable=True)


class Admin(Base):
    __tablename__ = "admins"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    role: Mapped[str] = mapped_column(String(30), default="project_admin")
    added_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
