import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import DATABASE_URL

# SQL loglari sukut bo'yicha O'CHIQ.
# Ilgari echo=True edi — har bir so'rov passenger.log ga yozilib, log fayl
# shishib ketardi va diagnostika qiyinlashardi (shaxsiy ma'lumot ham logda
# qolardi). Kerak bo'lganda .env ga SQL_ECHO=1 qo'yib yoqish mumkin.
SQL_ECHO = os.getenv("SQL_ECHO", "").strip().lower() in ("1", "true", "yes", "ha")

engine = create_async_engine(
    DATABASE_URL,
    echo=SQL_ECHO,
    pool_pre_ping=True,   # uzilib qolgan ulanishni avtomatik tiklaydi
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass
