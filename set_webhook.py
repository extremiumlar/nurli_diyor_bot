"""
Bir marta ishga tushiring:
  python set_webhook.py https://sizningdomen.uz/webhook
"""
import asyncio
import sys
from aiogram import Bot
from app.config import BOT_TOKEN

async def main():
    if len(sys.argv) < 2:
        print("Foydalanish: python set_webhook.py https://domen.uz/webhook")
        return

    webhook_url = sys.argv[1]
    bot = Bot(token=BOT_TOKEN)

    await bot.set_webhook(webhook_url)
    info = await bot.get_webhook_info()
    print(f"Webhook ulandi: {info.url}")
    await bot.session.close()

asyncio.run(main())
