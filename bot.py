import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN
from app.handlers.start import router as start_router
from app.handlers.jobseeker import router as jobseeker_router
from app.handlers.admin import router as admin_router


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        start_router,
        jobseeker_router,
        admin_router,
    )

    print("Bot ishga tushdi...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
