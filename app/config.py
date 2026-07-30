import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN      = os.getenv("BOT_TOKEN")
DATABASE_URL   = os.getenv("DATABASE_URL")
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID"))

# Majburiy obuna
CHANNEL_ID     = os.getenv("CHANNEL_ID")          # "-100xxxxxxxxx"
CHANNEL_LINK   = os.getenv("CHANNEL_LINK")         # "https://t.me/kanal_nomi"
INSTAGRAM_URL  = os.getenv("INSTAGRAM_URL")        # "https://instagram.com/sahifa"

# Channel reader bot
CHANNEL_BOT_TOKEN    = os.getenv("CHANNEL_BOT_TOKEN", "")
CHANNEL_BOT_OWNER_ID = int(os.getenv("CHANNEL_BOT_OWNER_ID", "0"))

# Gemini API (narkotik kontent filter uchun)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── AI baholash (Claude) ───────────────────────────────────────────────────
# .env ga ANTHROPIC_API_KEY qo'yilsa, yozma javoblar avtomatik baholanadi.
# Kalit bo'lmasa tizim avvalgidek ishlaydi (HR qo'lda baholaydi).
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "claude-haiku-4-5")

# Userbot (Telethon) — @funstat va boshqa botlarga so'rov yuborish uchun
TELEGRAM_API_ID        = int(os.getenv("TELEGRAM_API_ID", "0") or 0)
TELEGRAM_API_HASH      = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_USERBOT_PHONE = os.getenv("TELEGRAM_USERBOT_PHONE", "")
