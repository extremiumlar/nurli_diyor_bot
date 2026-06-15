import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    db_path: str
    default_lang: str


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN2", "8898353083:AAHV5z3s4jNyvM_j12OJDMk74-J4jOMGV5g").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN2 .env faylida ko'rsatilmagan")
    return Settings(
        bot_token=token,
        db_path=os.getenv("DB_PATH2", "admins_bot.db").strip() or "admins_bot.db",
        default_lang=os.getenv("DEFAULT_LANG", "uz").strip() or "uz",
    )


settings = load_settings()
