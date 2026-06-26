"""
Ikkinchi bot (channel_reader) webhookini o'chirish uchun bir marta ishga tushiring:
  python delete_webhook2.py
"""
import asyncio
from aiogram import Bot
from app.config import CHANNEL_BOT_TOKEN


async def main():
    if not CHANNEL_BOT_TOKEN:
        print("CHANNEL_BOT_TOKEN .env da topilmadi")
        return
    bot = Bot(token=CHANNEL_BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    info = await bot.get_webhook_info()
    print(f"Webhook o'chirildi. Hozirgi holat: url='{info.url}'")
    await bot.session.close()


asyncio.run(main())
