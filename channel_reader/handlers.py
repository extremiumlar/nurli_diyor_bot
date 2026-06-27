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

_TG_POST_RE = re.compile(r"t\.me/([a-zA-Z0-9_]+)/(\d+)", re.IGNORECASE)
_TG_CHANNEL_RE = re.compile(r"t\.me/([a-zA-Z0-9_]+)", re.IGNORECASE)
_INSTAGRAM_POST_RE = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)


# ── Telegram: bitta post ────────────────────────────────────────────────────
def _parse_tg_post(text: str) -> tuple[str, int] | None:
    m = _TG_POST_RE.search(text or "")
    if not m:
        return None
    return m.group(1), int(m.group(2))


async def _fetch_tg_post(channel: str, post_id: int) -> str | None:
    url = f"https://t.me/{channel}/{post_id}?embed=1"
    headers = {"User-Agent": _BROWSER_UA}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return None
            html = await resp.text()
    soup = BeautifulSoup(html, "html.parser")
    el = soup.select_one(".tgme_widget_message_text")
    return el.get_text("\n", strip=True) if el else None


# ── Telegram: kanal (oxirgi 10 ta post) ─────────────────────────────────────
def _parse_channel(text: str) -> str | None:
    text = text.strip()
    m = _TG_CHANNEL_RE.search(text)
    if m:
        return m.group(1)
    if text.startswith("@"):
        return text[1:]
    return None


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


# ── Instagram: bitta post (og:tag) ──────────────────────────────────────────
def _parse_instagram_post(text: str) -> str | None:
    m = _INSTAGRAM_POST_RE.search(text or "")
    return m.group(0) if m else None


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


# ── Handlers ────────────────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id != CHANNEL_BOT_OWNER_ID:
        return
    await message.answer(
        "Quyidagilardan birini yuboring:\n\n"
        "📢 <b>Telegram bitta post</b>: <code>https://t.me/channel/123</code>\n"
        "  → faqat o'sha postning matni\n\n"
        "📢 <b>Telegram kanal</b>: <code>https://t.me/channelname</code>\n"
        "  → oxirgi 10 ta post matni\n\n"
        "📸 <b>Instagram post/reel</b>: <code>https://instagram.com/p/XXX/</code>\n"
        "  → o'sha postning caption matni",
        parse_mode="HTML"
    )


@router.message()
async def handle_link(message: Message):
    if message.from_user.id != CHANNEL_BOT_OWNER_ID:
        return

    text = message.text or ""

    # 1) Telegram bitta post (kanal nomi + post ID)
    tg_post = _parse_tg_post(text)
    if tg_post:
        channel, post_id = tg_post
        await message.answer(f"⏳ <b>@{channel}</b>/{post_id} olinmoqda…", parse_mode="HTML")
        try:
            post_text = await _fetch_tg_post(channel, post_id)
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")
            return
        if not post_text:
            await message.answer("Post topilmadi yoki matnsiz (faqat media).")
            return
        await message.answer(post_text)
        return

    # 2) Instagram bitta post
    insta_url = _parse_instagram_post(text)
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

    # 3) Telegram kanal (oxirgi 10 ta post)
    channel = _parse_channel(text)
    if not channel:
        await message.answer(
            "❌ Link noto'g'ri. Misol:\n"
            "• https://t.me/channel/123 (bitta post)\n"
            "• https://t.me/channelname (oxirgi 10 ta post)\n"
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
    for i, ttext in enumerate(posts, 1):
        await message.answer(f"<b>#{i}</b>\n{ttext}", parse_mode="HTML")
        await asyncio.sleep(0.3)
