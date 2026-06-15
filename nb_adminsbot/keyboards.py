from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from .utils import REACTION_PRESETS, chunk


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Yangi post"), KeyboardButton(text="📡 Mening kanallarim")],
            [KeyboardButton(text="➕ Kanal qo'shish"), KeyboardButton(text="ℹ️ Yordam")],
        ],
        resize_keyboard=True,
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True,
    )


def channels_list_kb(channels: list, action: str = "pick") -> InlineKeyboardMarkup:
    rows = []
    for ch in channels:
        title = ch["title"]
        rows.append([
            InlineKeyboardButton(text=f"📡 {title}", callback_data=f"{action}:{ch['chat_id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows or [[
        InlineKeyboardButton(text="—", callback_data="noop")
    ]])


def channel_actions_kb(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Kanalni o'chirish", callback_data=f"chdel:{chat_id}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="chback")],
    ])


def post_editor_kb(
    *,
    silent: bool,
    has_buttons: bool,
    has_reactions: bool,
    has_media: bool,
    show_more: bool,
) -> InlineKeyboardMarkup:
    base = [
        [InlineKeyboardButton(
            text=("📎 Medianı o'zgartirish" if has_media else "📎 Mediafayl biriktirish"),
            callback_data="ed:media"
        )],
        [InlineKeyboardButton(
            text=("💬 Izohlarni o'chirish" if False else "💬 Izoh qo'shish"),
            callback_data="ed:comments"
        )],
        [InlineKeyboardButton(text="💬 Add Native Comments", callback_data="ed:native_comments")],
        [InlineKeyboardButton(
            text=("👍 Reaksiyalarni o'zgartirish" if has_reactions else "👍 Reaksiyalar qo'shish"),
            callback_data="ed:reactions"
        )],
        [InlineKeyboardButton(
            text=("🔗 Tugmalarni o'zgartirish" if has_buttons else "🔗 URL-tugmalar qo'shish"),
            callback_data="ed:buttons"
        )],
        [InlineKeyboardButton(
            text=("🔔 Ovoz bilan yuborish" if silent else "🔕 Ovozsiz yuborish"),
            callback_data="ed:silent"
        )],
        [InlineKeyboardButton(text="🗑 Postni o'chirish", callback_data="ed:discard")],
    ]
    if show_more:
        base.extend([
            [InlineKeyboardButton(text="📌 Postni pin qilish (kanalda)", callback_data="ed:pin")],
            [InlineKeyboardButton(text="🚫 Old-ko'rinishni o'chirish", callback_data="ed:nopreview")],
            [InlineKeyboardButton(text="⬆️ Kamroq ko'rsatish", callback_data="ed:less")],
        ])
    else:
        base.append([InlineKeyboardButton(text="⬇ Ko'proq ko'rsatish", callback_data="ed:more")])

    base.append([
        InlineKeyboardButton(text="✅ Nashr etish", callback_data="ed:publish"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="ed:cancel"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=base)


def reactions_picker_kb(selected: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for group in chunk(REACTION_PRESETS, 4):
        rows.append([
            InlineKeyboardButton(
                text=(f"✅{e}" if e in selected else e),
                callback_data=f"rxpick:{e}",
            )
            for e in group
        ])
    rows.append([
        InlineKeyboardButton(text="🧹 Tozalash", callback_data="rxpick:clear"),
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="rxpick:done"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_publish_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, nashr eting", callback_data="pubok"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="pubno"),
        ]
    ])
