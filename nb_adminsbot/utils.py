from __future__ import annotations

import re
from typing import Iterable, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity, WebAppInfo


URL_RE = re.compile(r"^(https?://|tg://|t\.me/|@)", re.IGNORECASE)

COLOR_EMOJI: dict[str, str] = {
    "r": "🔴",
    "g": "🟢",
    "y": "🟡",
    "b": "🔵",
    "p": "🟣",
    "o": "🟠",
    "k": "⚫",
    "w": "⚪",
}

COLOR_SQUARE: dict[str, str] = {
    "r": "🟥",
    "g": "🟩",
    "y": "🟨",
    "b": "🟦",
    "p": "🟪",
    "o": "🟧",
    "k": "⬛",
    "w": "⬜",
}

UZ_COLOR_CODES: dict[str, str] = {
    "Q": "r",
    "Y": "g",
    "S": "y",
    "K": "b",
    "B": "p",
    "T": "o",
    "QR": "k",
    "O": "w",
}

COLOR_ALIASES: dict[str, str] = {
    "r": "r", "red": "r", "qizil": "r",
    "g": "g", "green": "g", "yashil": "g",
    "y": "y", "yellow": "y", "sariq": "y",
    "b": "b", "blue": "b", "kok": "b", "ko'k": "b",
    "p": "p", "purple": "p", "binafsha": "p",
    "o": "o", "orange": "o", "toqsariq": "o", "to'q sariq": "o",
    "k": "k", "black": "k", "qora": "k",
    "w": "w", "white": "w", "oq": "w",
}

COLOR_MARKER_RE = re.compile(r"^\s*\[([^\]]+)\]\s*", re.IGNORECASE)


def _extract_markers(label: str) -> tuple[str, Optional[str], Optional[str], bool]:
    is_webapp = False
    prefix: Optional[str] = None
    suffix: Optional[str] = None

    while True:
        m = COLOR_MARKER_RE.match(label)
        if not m:
            break
        raw = m.group(1).strip()

        if raw.lower() == "app":
            is_webapp = True
            label = label[m.end():].strip()
            continue

        full_mode = raw.endswith("!")
        bare = raw[:-1].strip() if full_mode else raw

        code = UZ_COLOR_CODES.get(bare)
        if not code:
            code = COLOR_ALIASES.get(bare.lower())
        if not code:
            break

        if full_mode:
            sq = COLOR_SQUARE[code]
            prefix = f"{sq}{sq}"
            suffix = f"{sq}{sq}"
        else:
            prefix = COLOR_EMOJI[code]
            suffix = None

        label = label[m.end():].strip()

    return label, prefix, suffix, is_webapp


def _extract_color(label: str) -> tuple[str, Optional[str], Optional[str]]:
    clean, p, s, _ = _extract_markers(label)
    return clean, p, s


def parse_url_buttons(text: str) -> tuple[list[list[InlineKeyboardButton]], list[str]]:
    rows: list[list[InlineKeyboardButton]] = []
    errors: list[str] = []

    for ln_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        row: list[InlineKeyboardButton] = []
        for part in line.split("|"):
            part = part.strip()
            if not part:
                continue
            if " - " not in part:
                errors.append(f"{ln_no}-qator: '{part}' — format 'Matn - URL'")
                continue
            label, _, url = part.partition(" - ")
            label = label.strip()
            url = url.strip()
            if not label or not url:
                errors.append(f"{ln_no}-qator: matn yoki URL bo'sh")
                continue
            if not URL_RE.match(url):
                errors.append(f"{ln_no}-qator: '{url}' to'g'ri URL emas")
                continue
            if url.startswith("@"):
                url = f"https://t.me/{url[1:]}"
            elif url.startswith("t.me/"):
                url = f"https://{url}"

            label_clean, prefix, suffix, is_webapp = _extract_markers(label)
            if prefix and suffix and label_clean:
                final_label = f"{prefix} {label_clean} {suffix}"
            elif prefix and label_clean:
                final_label = f"{prefix} {label_clean}"
            elif prefix:
                final_label = prefix
            else:
                final_label = label_clean or label

            try:
                if is_webapp and url.lower().startswith("https://"):
                    row.append(InlineKeyboardButton(
                        text=final_label,
                        web_app=WebAppInfo(url=url),
                    ))
                else:
                    if is_webapp:
                        errors.append(
                            f"{ln_no}-qator: [app] uchun HTTPS URL kerak — "
                            f"oddiy URL-tugma sifatida qo'yildi"
                        )
                    row.append(InlineKeyboardButton(text=final_label, url=url))
            except Exception as e:
                errors.append(f"{ln_no}-qator: {e}")
        if row:
            rows.append(row)

    return rows, errors


def build_post_keyboard(
    url_rows: list[list[InlineKeyboardButton]],
    reactions: list[str],
    post_id: Optional[int] = None,
    counts: Optional[dict[str, int]] = None,
) -> Optional[InlineKeyboardMarkup]:
    counts = counts or {}
    rows: list[list[InlineKeyboardButton]] = []

    if reactions:
        reaction_row: list[InlineKeyboardButton] = []
        for emoji in reactions:
            cnt = counts.get(emoji, 0)
            label = f"{emoji} {cnt}" if cnt else emoji
            cb = f"react:{post_id}:{emoji}" if post_id else f"react_preview:{emoji}"
            reaction_row.append(InlineKeyboardButton(text=label, callback_data=cb))
        rows.append(reaction_row)

    rows.extend(url_rows)

    if not rows:
        return None
    return InlineKeyboardMarkup(inline_keyboard=rows)


REACTION_PRESETS: list[str] = [
    "👍", "👎", "❤", "🔥", "🥰", "👏", "😁", "🤔",
    "🎉", "🤩", "💯", "⚡", "🆒", "🙏", "👌", "😍",
]


def chunk(items: list, size: int) -> Iterable[list]:
    for i in range(0, len(items), size):
        yield items[i:i + size]


def restore_entities(entity_dicts: Optional[list[dict]]) -> Optional[list[MessageEntity]]:
    if not entity_dicts:
        return None
    out: list[MessageEntity] = []
    for d in entity_dicts:
        try:
            out.append(MessageEntity.model_validate(d))
        except Exception:
            continue
    return out or None
