import sys
import os
import json
import asyncio

sys.path.insert(0, os.path.dirname(__file__))

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from app.config import BOT_TOKEN
from app.fsm_storage import SQLiteFSMStorage
from app.database.connect import engine, Base
from app.database import models  # noqa
from app.handlers.start import router as start_router
from app.handlers.jobseeker import router as jobseeker_router
from app.handlers.admin import router as admin_router

# ── Bot va event loop — bir marta yaratiladi ───────────────────────────────
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

_DB_PATH = os.path.join(os.path.dirname(__file__), "bot.db")

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=SQLiteFSMStorage(_DB_PATH))
dp.include_routers(start_router, jobseeker_router, admin_router)

# DB jadvallarni yaratish (agar yo'q bo'lsa)
async def _init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

loop.run_until_complete(_init_db())


# ── WSGI application ───────────────────────────────────────────────────────
def application(environ, start_response):
    path   = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if path == "/webhook" and method == "POST":
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
            body   = environ["wsgi.input"].read(length)
            update = Update.model_validate(json.loads(body))
            loop.run_until_complete(dp.feed_update(bot, update))
        except Exception as e:
            print(f"[WEBHOOK ERROR] {e}", file=sys.stderr)

        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"ok"]

    # Boshqa so'rovlar
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"Bot is running"]
