import asyncio
import html as html_lib
import re
import aiohttp
from bs4 import BeautifulSoup
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import CHANNEL_BOT_OWNER_ID

router = Router()

_FB_UA = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
_BROWSER_UA = "Mozilla/5.0"

_INSTAGRAM_RE = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)


def _parse_channel(text: str) -> str | None:
    text = text.strip()
    m = re.search(r"t\.me/([a-zA-Z0-9_]+)", text)
    if m:
        return m.group(1)
    if text.startswith("@"):
        return text[1:]
    return None


def _parse_instagram(text: str) -> str | None:
    m = _INSTAGRAM_RE.search(text or "")
    return m.group(0) if m else None


async def _fetch_posts(channel: str, limit: int = 10) -> list[str]:
    url = f"https://t.me/s/{channel}"
    headers = {"User-Agent": _BROWSER_UA}
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


async def _fetch_instagram_caption(url: str) -> dict | None:
    headers = {"User-Agent": _FB_UA}
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers, allow_redirects=True) as resp:
            if resp.status != 200:
                return None
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")
    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    return {
        "title": og_title["content"] if og_title and og_title.get("content") else None,
        "description": og_desc["content"] if og_desc and og_desc.get("content") else None,
    }


@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id != CHANNEL_BOT_OWNER_ID:
        return
    await message.answer(
        "Telegram kanal yoki Instagram post linkini yuboring.\n\n"
        "📢 Telegram: <code>https://t.me/channelname</code> — oxirgi 10 ta post\n"
        "📸 Instagram: <code>https://instagram.com/p/XXX/</code> yoki "
        "<code>https://instagram.com/reel/XXX/</code> — post caption matni",
        parse_mode="HTML"
    )


@router.message()
async def handle_link(message: Message):
    if message.from_user.id != CHANNEL_BOT_OWNER_ID:
        return

    text = message.text or ""

    insta_url = _parse_instagram(text)
    if insta_url:
        await message.answer("⏳ Instagram postdan matn olinmoqda…")
        try:
            data = await _fetch_instagram_caption(insta_url)
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")
            return

        if not data or (not data["title"] and not data["description"]):
            await message.answer(
                "Postdan matn olib bo'lmadi. Post private bo'lishi yoki "
                "Instagram bizni vaqtincha bloklagan bo'lishi mumkin."
            )
            return

        parts = ["📸 <b>Instagram post</b>"]
        if data["title"]:
            parts.append(f"\n<b>Sarlavha:</b>\n{html_lib.escape(data['title'])}")
        if data["description"]:
            parts.append(f"\n<b>Tavsif:</b>\n{html_lib.escape(data['description'])}")
        await message.answer("\n".join(parts), parse_mode="HTML")
        return

    channel = _parse_channel(text)
    if not channel:
        await message.answer(
            "❌ Link noto'g'ri. Misol:\n"
            "• https://t.me/channelname\n"
            "• https://instagram.com/p/XXX/"
        )
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
