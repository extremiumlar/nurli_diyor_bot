from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.config import CHANNEL_ID
from app.database.crud import create_or_update_user, get_user, update_user_role
from app.keyboards.inline import role_keyboard, subscribe_keyboard
from app.keyboards.reply import client_menu, jobseeker_menu

router = Router()

async def check_subscription(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot):
    is_subscribed = await check_subscription(bot, message.from_user.id)

    if not is_subscribed:
        await message.answer(
            "Botdan foydalanish uchun avval kanalga obuna bo‘ling.",
            reply_markup=subscribe_keyboard()
        )
        return

    user = await create_or_update_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    if user.role == "client":
        await message.answer("Mijoz menyusi:", reply_markup=client_menu())
    elif user.role == "jobseeker":
        await message.answer("Ish izlovchi menyusi:", reply_markup=jobseeker_menu())
    else:
        await message.answer("Rolingizni tanlang:", reply_markup=role_keyboard())

@router.callback_query(lambda c: c.data == "check_subscribe")
async def check_subscribe_callback(callback: CallbackQuery, bot: Bot):
    is_subscribed = await check_subscription(bot, callback.from_user.id)

    if not is_subscribed:
        await callback.answer("Hali kanalga obuna bo‘lmagansiz.", show_alert=True)
        return

    await create_or_update_user(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name
    )

    await callback.message.answer("Rolingizni tanlang:", reply_markup=role_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("role:"))
async def role_callback(callback: CallbackQuery):
    role = callback.data.split(":")[1]

    await update_user_role(callback.from_user.id, role)

    if role == "client":
        await callback.message.answer("Siz mijoz sifatida ro‘yxatdan o‘tdingiz.", reply_markup=client_menu())
    elif role == "jobseeker":
        await callback.message.answer("Siz ish izlovchi sifatida ro‘yxatdan o‘tdingiz.", reply_markup=jobseeker_menu())

    await callback.answer()