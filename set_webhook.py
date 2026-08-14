"""
Bir marta ishga tushiring:
  python set_webhook.py https://sizningdomen.uz/webhook
"""
import asyncio
import sys
from aiogram import Bot
from app.config import BOT_TOKEN, WEBHOOK_SECRET

async def main():
    if len(sys.argv) < 2:
        print("Foydalanish: python set_webhook.py https://domen.uz/webhook")
        return

    webhook_url = sys.argv[1]
    bot = Bot(token=BOT_TOKEN)

    # secret_token — Telegram har so'rovda X-Telegram-Bot-Api-Secret-Token
    # sarlavhasida qaytaradi; WSGI shuni tekshiradi (S1, tahlil/S1.md).
    await bot.set_webhook(webhook_url, secret_token=WEBHOOK_SECRET or None)
    info = await bot.get_webhook_info()
    print(f"Webhook ulandi: {info.url}")
    print(f"Secret himoyasi: {'YOQILGAN' if WEBHOOK_SECRET else 'OCHIQ (WEBHOOK_SECRET yo`q)'}")
    await bot.session.close()

asyncio.run(main())
