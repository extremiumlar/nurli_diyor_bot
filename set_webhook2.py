"""
Ikkinchi botni webhookga ulash uchun bir marta ishga tushiring:
  python set_webhook2.py
"""
import asyncio
from nb_adminsbot.config import settings
from aiogram import Bot

WEBHOOK_URL = "https://bulutliiqtisodiyot.uz/webhook2"


async def main():
    bot = Bot(token=settings.bot_token)
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    info = await bot.get_webhook_info()
    print(f"Webhook ulandi: {info.url}")
    await bot.session.close()


asyncio.run(main())
