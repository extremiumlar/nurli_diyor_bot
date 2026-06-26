"""
Ikkinchi botni (channel_reader) webhookga ulash uchun bir marta ishga tushiring:
  python set_webhook2.py
"""
import asyncio
from aiogram import Bot
from app.config import CHANNEL_BOT_TOKEN

WEBHOOK_URL = "https://bulutliiqtisodiyot.uz/webhook2"


async def main():
    if not CHANNEL_BOT_TOKEN:
        print("CHANNEL_BOT_TOKEN .env da topilmadi")
        return
    bot = Bot(token=CHANNEL_BOT_TOKEN)
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    info = await bot.get_webhook_info()
    print(f"Webhook ulandi: {info.url}")
    await bot.session.close()


asyncio.run(main())
