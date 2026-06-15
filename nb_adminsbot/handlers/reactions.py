from __future__ import annotations

import json

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery

from .. import database as db_mod
from ..utils import build_post_keyboard, parse_url_buttons


router = Router(name="nb2_reactions")


@router.callback_query(F.data.startswith("react:"))
async def on_reaction(cb: CallbackQuery, bot: Bot) -> None:
    try:
        _, post_id_s, emoji = cb.data.split(":", 2)
        post_id = int(post_id_s)
    except (ValueError, IndexError):
        await cb.answer("Format xato")
        return

    async with db_mod.db().execute("SELECT * FROM posts WHERE id = ?", (post_id,)) as cur:
        post = await cur.fetchone()
    if not post:
        await cb.answer("Post topilmadi", show_alert=True)
        return

    reactions = json.loads(post["reactions_json"] or "[]")
    if emoji not in reactions:
        await cb.answer("Reaksiya mavjud emas")
        return

    result = await db_mod.toggle_reaction(post_id, cb.from_user.id, emoji)
    counts = result["counts"]

    existing_kb = cb.message.reply_markup
    url_rows = []
    if existing_kb:
        for row in existing_kb.inline_keyboard:
            if row and (row[0].url or row[0].web_app):
                url_rows.append(row)

    new_kb = build_post_keyboard(url_rows, reactions, post_id=post_id, counts=counts)
    try:
        await bot.edit_message_reply_markup(
            chat_id=post["chat_id"],
            message_id=post["message_id"],
            reply_markup=new_kb,
        )
    except TelegramAPIError:
        pass

    pick = result["user_pick"]
    await cb.answer(f"Sizning ovozingiz: {pick}" if pick else "Ovoz olib tashlandi")


@router.callback_query(F.data == "noop")
async def noop(cb: CallbackQuery) -> None:
    await cb.answer()


@router.callback_query(F.data.startswith("react_preview:"))
async def react_preview(cb: CallbackQuery) -> None:
    await cb.answer("Bu old-ko'rinish. Nashrdan keyin ishlaydi.")
