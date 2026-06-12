from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.database.crud import create_or_update_user
from app.keyboards.reply import main_menu

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot):
    await create_or_update_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )
    await message.answer(
        "👋 <b>Xush kelibsiz!</b>\nQuyidagi bo'limlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )
