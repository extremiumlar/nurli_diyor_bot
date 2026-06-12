from typing import Callable, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from app.database.crud import get_user
from app.keyboards.inline import role_keyboard


class RoleCheckMiddleware(BaseMiddleware):
    EXEMPT_COMMANDS = {"/start", "/admin", "/addadmin", "/removeadmin", "/stats", "/export_leads"}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        text = event.text or ""
        if text.split()[0] in self.EXEMPT_COMMANDS if text else True:
            if text and text.split()[0] in self.EXEMPT_COMMANDS:
                return await handler(event, data)

        user = await get_user(event.from_user.id)
        if user and not user.role and text not in self.EXEMPT_COMMANDS:
            await event.answer("Iltimos, avval rolingizni tanlang:", reply_markup=role_keyboard())
            return

        return await handler(event, data)
