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

from nb_adminsbot import database as nb2_db
from nb_adminsbot.config import settings as nb2_settings
from nb_adminsbot.handlers.start import router as nb2_start_router
from nb_adminsbot.handlers.channels import router as nb2_channels_router
from nb_adminsbot.handlers.post import router as nb2_post_router
from nb_adminsbot.handlers.reactions import router as nb2_reactions_router

# ── Yagona event loop — barcha botlar uchun ───────────────────────────────
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

_BASE_DIR = os.path.dirname(__file__)
_DB_PATH  = os.path.join(_BASE_DIR, "bot.db")
_DB_PATH2 = os.path.join(_BASE_DIR, "admins_bot.db")
_FSM_DB2  = os.path.join(_BASE_DIR, "admins_fsm.db")

# ── Bot 1: HR bot ─────────────────────────────────────────────────────────
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=SQLiteFSMStorage(_DB_PATH))
dp.include_routers(start_router, jobseeker_router, admin_router)

async def _init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

loop.run_until_complete(_init_db())

# ── Bot 2: Admins channel-post bot ────────────────────────────────────────
bot2 = Bot(token=nb2_settings.bot_token)
dp2  = Dispatcher(storage=SQLiteFSMStorage(_FSM_DB2))
dp2.include_routers(nb2_start_router, nb2_channels_router, nb2_post_router, nb2_reactions_router)

loop.run_until_complete(nb2_db.init_db(_DB_PATH2))


# ── WSGI application ───────────────────────────────────────────────────────
def application(environ, start_response):
    path   = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if method == "POST":
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
            body   = environ["wsgi.input"].read(length)
            update = Update.model_validate(json.loads(body))

            if path == "/webhook":
                loop.run_until_complete(dp.feed_update(bot, update))
            elif path == "/webhook2":
                loop.run_until_complete(dp2.feed_update(bot2, update))
        except Exception as e:
            print(f"[WEBHOOK ERROR] {path} {e}", file=sys.stderr)

        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"ok"]

    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"Bot is running"]
