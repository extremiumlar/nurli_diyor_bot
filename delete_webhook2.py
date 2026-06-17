"""
nb_adminsbot webhookini o'chirish uchun bir marta ishga tushiring:
  python delete_webhook2.py
"""
import asyncio
from aiogram import Bot

BOT2_TOKEN = "8898353083:AAHV5z3s4jNyvM_j12OJDMk74-J4jOMGV5g"


async def main():
    bot = Bot(token=BOT2_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    info = await bot.get_webhook_info()
    print(f"Webhook o'chirildi. Hozirgi holat: url='{info.url}'")
    await bot.session.close()


asyncio.run(main())
