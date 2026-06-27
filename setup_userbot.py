"""
Userbot uchun session yaratish. Bir marta ishga tushiring:
  python setup_userbot.py

Skript Telegram'dan kelgan kodni so'raydi (SMS yoki Telegram app orqali).
2FA yoqilgan bo'lsa parolni ham so'raydi.
Yakuniy 'userbot.session' fayli loyiha papkasida saqlanadi.
"""
import asyncio
import sys

from telethon import TelegramClient

from app.config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_USERBOT_PHONE
from userbot.client import SESSION_PATH


async def main():
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        print("XATO: TELEGRAM_API_ID va TELEGRAM_API_HASH .env'da bo'lishi kerak", file=sys.stderr)
        sys.exit(1)

    phone = TELEGRAM_USERBOT_PHONE
    if not phone:
        phone = input("Telefon raqami (+998...): ").strip()

    client = TelegramClient(SESSION_PATH, TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.start(phone=phone)
    me = await client.get_me()
    print(f"\n[OK] Login: {me.first_name} {(me.last_name or '')} "
          f"(@{me.username or 'no-username'})")
    print(f"     User ID: {me.id}")
    print(f"     Session: {SESSION_PATH}.session")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
