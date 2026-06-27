import asyncio
import html as html_lib
import os
import re

import aiohttp
import instaloader
from bs4 import BeautifulSoup
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from instaloader import Profile

from app.config import (
    CHANNEL_BOT_OWNER_ID,
    INSTAGRAM_USER,
    INSTAGRAM_PASS,
)

router = Router()

_FB_UA = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
_BROWSER_UA = "Mozilla/5.0"

_INSTAGRAM_POST_RE = re.compile(
    r"https?://(?:www\.)?instagram\.com/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)
_INSTAGRAM_PROFILE_RE = re.compile(
    r"https?://(?:www\.)?instagram\.com/([A-Za-z0-9._]+)/?",
    re.IGNORECASE,
)
_RESERVED_IG = {
    "p", "reel", "reels", "tv", "stories", "explore", "directory",
    "accounts", "challenge", "developer", "web", "about", "legal",
}

_SESSION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SESSION_FILE = os.path.join(_SESSION_DIR, f".instaloader-session-{INSTAGRAM_USER}")

_loader: instaloader.Instaloader | None = None
_login_lock = asyncio.Lock()


# ── Telegram channel ────────────────────────────────────────────────────────
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


# ── Instagram: single post (og:tag orqali) ──────────────────────────────────
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


# ── Instagram: profile last N posts (instaloader orqali) ────────────────────
def _parse_instagram_profile(text: str) -> str | None:
    if _INSTAGRAM_POST_RE.search(text or ""):
        return None
    m = _INSTAGRAM_PROFILE_RE.search(text or "")
    if not m:
        return None
    username = m.group(1).strip("/")
    if username.lower() in _RESERVED_IG:
        return None
    return username


def _build_loader() -> instaloader.Instaloader:
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
    )
    if INSTAGRAM_USER and os.path.exists(_SESSION_FILE):
        try:
            L.load_session_from_file(INSTAGRAM_USER, _SESSION_FILE)
            return L
        except Exception:
            pass
    if INSTAGRAM_USER and INSTAGRAM_PASS:
        L.login(INSTAGRAM_USER, INSTAGRAM_PASS)
        try:
            L.save_session_to_file(_SESSION_FILE)
        except Exception:
            pass
    return L


async def _get_loader() -> instaloader.Instaloader:
    global _loader
    if _loader is not None:
        return _loader
    async with _login_lock:
        if _loader is None:
            loop = asyncio.get_event_loop()
            _loader = await loop.run_in_executor(None, _build_loader)
    return _loader


def _fetch_user_posts_sync(L: instaloader.Instaloader, username: str, limit: int) -> list[dict]:
    profile = Profile.from_username(L.context, username)
    posts = []
    for i, post in enumerate(profile.get_posts()):
        if i >= limit:
            break
        posts.append({
            "caption": post.caption or "",
            "shortcode": post.shortcode,
            "date": post.date_utc.strftime("%Y-%m-%d"),
        })
    return posts


async def _fetch_user_posts(username: str, limit: int = 3) -> list[dict]:
    L = await _get_loader()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_user_posts_sync, L, username, limit)


# ── Handlers ────────────────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id != CHANNEL_BOT_OWNER_ID:
        return
    await message.answer(
        "Quyidagilardan birini yuboring:\n\n"
        "📢 <b>Telegram kanal</b>: <code>https://t.me/channelname</code>\n"
        "  → oxirgi 10 ta post matni\n\n"
        "📸 <b>Instagram post/reel</b>: <code>https://instagram.com/p/XXX/</code>\n"
        "  → o'sha postning caption matni\n\n"
        "👤 <b>Instagram profil</b>: <code>https://instagram.com/username/</code>\n"
        "  → profilning oxirgi 3 ta postining matni",
        parse_mode="HTML"
    )


@router.message()
async def handle_link(message: Message):
    if message.from_user.id != CHANNEL_BOT_OWNER_ID:
        return

    text = message.text or ""

    # 1) Instagram bitta post URL
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

    # 2) Instagram profil URL → oxirgi 3 ta post
    ig_username = _parse_instagram_profile(text)
    if ig_username:
        await message.answer(
            f"⏳ <b>@{ig_username}</b> profilining oxirgi 3 ta posti olinmoqda…\n"
            "(login + scraping biroz vaqt olishi mumkin)",
            parse_mode="HTML",
        )
        try:
            posts = await _fetch_user_posts(ig_username, limit=3)
        except instaloader.exceptions.ProfileNotExistsException:
            await message.answer(f"❌ <b>@{ig_username}</b> topilmadi.", parse_mode="HTML")
            return
        except instaloader.exceptions.LoginRequiredException:
            await message.answer(
                "❌ Login talab qilinmoqda — server akkauntdan login bo'la olmadi. "
                "Local'da session yarating va serverga ko'chiring."
            )
            return
        except instaloader.exceptions.BadCredentialsException:
            await message.answer("❌ Instagram login/parol noto'g'ri.")
            return
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            await message.answer(
                "❌ Instagram 2FA so'rayapti. Botda 2FA kodini kiritib bo'lmaydi — "
                "local'dan session ko'chirish kerak."
            )
            return
        except instaloader.exceptions.ConnectionException as e:
            await message.answer(f"❌ Instagram bog'lanishda xatolik: {e}")
            return
        except Exception as e:
            await message.answer(f"❌ Xatolik: {type(e).__name__}: {e}")
            return

        if not posts:
            await message.answer("Postlar topilmadi yoki profil bo'sh.")
            return

        await message.answer(
            f"📋 <b>@{ig_username}</b> — oxirgi {len(posts)} ta post:",
            parse_mode="HTML",
        )
        for i, p in enumerate(posts, 1):
            caption = p["caption"] or "<i>(caption yo'q)</i>"
            url = f"https://instagram.com/p/{p['shortcode']}/"
            body = (
                f"<b>#{i}</b> — {p['date']}\n"
                f"{url}\n\n"
                f"{html_lib.escape(p['caption']) if p['caption'] else '<i>(caption yoq)</i>'}"
            )
            # Telegram cheklov: 4096 belgi
            if len(body) > 4000:
                body = body[:4000] + "…"
            await message.answer(body, parse_mode="HTML", disable_web_page_preview=True)
            await asyncio.sleep(0.5)
        return

    # 3) Telegram kanal
    channel = _parse_channel(text)
    if not channel:
        await message.answer(
            "❌ Link noto'g'ri. Misol:\n"
            "• https://t.me/channelname\n"
            "• https://instagram.com/p/XXX/\n"
            "• https://instagram.com/username/"
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
