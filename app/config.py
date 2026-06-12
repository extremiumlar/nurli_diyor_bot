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
