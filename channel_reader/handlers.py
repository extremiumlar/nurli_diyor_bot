import asyncio
import re
import aiohttp
from bs4 import BeautifulSoup
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import CHANNEL_BOT_OWNER_ID

router = Router()


def _parse_channel(text: str) -> str | None:
    text = text.strip()
    m = re.search(r"t\.me/([a-zA-Z0-9_]+)", text)
    if m:
        return m.group(1)
    if text.startswith("@"):
        return text[1:]
    return None


async def _fetch_posts(channel: str, limit: int = 10) -> list[str]:
    url = f"https://t.me/s/{channel}"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return []
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")
    messages = soup.select(".tgme_widget_message")
    texts = []
    for msg in messages:
        el = msg.select_one(".tgme_widget_message_text")
        if el:
            texts.append(el.get_text("\n", strip=True))
    return texts[-limit:]


@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id != CHANNEL_BOT_OWNER_ID:
        return
    await message.answer(
        "Kanal linkini yuboring.\n"
        "Masalan: <code>https://t.me/channelname</code>\n\n"
        "Oxirgi 10 ta postning textini olasiz.",
        parse_mode="HTML"
    )


@router.message()
async def handle_link(message: Message):
    if message.from_user.id != CHANNEL_BOT_OWNER_ID:
        return
    channel = _parse_channel(message.text or "")
    if not channel:
        await message.answer("❌ Kanal linki noto'g'ri. Masalan: https://t.me/channelname")
        return

    await message.answer(f"⏳ <b>@{channel}</b> kanalidan postlar olinmoqda…", parse_mode="HTML")

    try:
        posts = await _fetch_posts(channel)
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
        return

    if not posts:
        await message.answer("Postlar topilmadi. Kanal private yoki mavjud emas.")
        return

    await message.answer(f"📋 <b>Oxirgi {len(posts)} ta post:</b>", parse_mode="HTML")
    for i, text in enumerate(posts, 1):
        await message.answer(f"<b>#{i}</b>\n{text}", parse_mode="HTML")
        await asyncio.sleep(0.3)
