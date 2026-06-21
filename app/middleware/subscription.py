from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        bot = data.get("bot")

        # Foydalanuvchi ID ni aniqlaymiz
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            # Obuna tekshirish callbackini to'xtatmaslik kerak
            if event.data == "check_subscribe":
                return await handler(event, data)
            user_id = event.from_user.id if event.from_user else None
        else:
            return await handler(event, data)

        if not user_id:
            return await handler(event, data)

        # Adminlarni tekshirishsiz o'tkazib yuborish
        from app.config import SUPER_ADMIN_ID
        if user_id == SUPER_ADMIN_ID:
            return await handler(event, data)
        from app.database.crud import get_admin
        if await get_admin(user_id):
            return await handler(event, data)

        # Kanal sozlamasini olamiz
        from app.database.crud import get_setting
        channel_id_str = await get_setting("channel_id")
        if not channel_id_str:
            return await handler(event, data)

        # A'zolikni tekshiramiz
        try:
            from aiogram.types import ChatMemberLeft, ChatMemberBanned
            member = await bot.get_chat_member(int(channel_id_str), user_id)
            if isinstance(member, (ChatMemberLeft, ChatMemberBanned)):
                await _send_not_subscribed(event, bot)
                return
        except Exception:
            # Kanal topilmasa yoki xatolik bo'lsa — o'tkazib yuboramiz
            return await handler(event, data)

        return await handler(event, data)


async def _send_not_subscribed(event, bot):
    from app.database.crud import get_setting
    from app.keyboards.inline import not_subscribed_keyboard

    channel_link = await get_setting("channel_link") or "https://t.me/channel"
    instagram    = await get_setting("instagram_link")
    kb           = not_subscribed_keyboard(channel_link, instagram)

    text = (
        "🔔 <b>Botdan foydalanish uchun kanalimizga obuna bo'ling!</b>\n\n"
        "Obuna bo'lgandan so'ng «✅ Obuna bo'ldim — tekshirish» tugmasini bosing."
    )

    if isinstance(event, Message):
        await event.answer(text, parse_mode="HTML", reply_markup=kb)
    elif isinstance(event, CallbackQuery):
        await event.message.answer(text, parse_mode="HTML", reply_markup=kb)
        await event.answer()
