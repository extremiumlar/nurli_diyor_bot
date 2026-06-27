"""Telethon userbot — @funstat va boshqa botlarga so'rov yuborish."""
import asyncio
import logging
import os

from app.config import TELEGRAM_API_ID, TELEGRAM_API_HASH

logger = logging.getLogger(__name__)

SESSION_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "userbot"  # Telethon avtomatik .session qo'shadi
)

_client = None
_init_lock = asyncio.Lock()


async def get_client():
    """Ulangan va autentifikatsiyadan o'tgan TelegramClient'ni qaytaradi yoki None."""
    global _client
    from telethon import TelegramClient

    if _client is not None and _client.is_connected():
        return _client

    async with _init_lock:
        if _client is not None and _client.is_connected():
            return _client
        if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
            logger.warning("Userbot uchun API_ID/API_HASH .env'da o'rnatilmagan")
            return None
        client = TelegramClient(SESSION_PATH, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            logger.warning("Userbot session yaroqsiz — setup_userbot.py'ni ishga tushiring")
            return None
        _client = client
    return _client


async def query_bot(bot_username: str, query_text: str, timeout: float = 20.0) -> str | None:
    """Botga xabar yuborib, javobini qaytaradi. Javob bo'lmasa None."""
    from telethon import events

    client = await get_client()
    if client is None:
        raise RuntimeError("Userbot tayyor emas. setup_userbot.py'ni ishga tushiring.")

    entity = await client.get_entity(bot_username)

    loop = asyncio.get_event_loop()
    future = loop.create_future()

    async def handler(event):
        if future.done():
            return
        text = event.message.text or event.message.message or ""
        if text.strip():
            future.set_result(text)

    client.add_event_handler(
        handler, events.NewMessage(chats=entity.id, incoming=True)
    )

    try:
        await client.send_message(entity, query_text)
        return await asyncio.wait_for(future, timeout=timeout)
    except asyncio.TimeoutError:
        return None
    finally:
        try:
            client.remove_event_handler(handler)
        except Exception:
            pass


async def query_funstat(username: str, timeout: float = 20.0) -> str | None:
    """@funstat ga username yuborib, javobini qaytaradi."""
    username = username.strip().lstrip("@")
    if not username:
        return None
    return await query_bot("@funstat", f"@{username}", timeout=timeout)
