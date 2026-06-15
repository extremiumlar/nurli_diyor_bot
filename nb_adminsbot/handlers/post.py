from __future__ import annotations

from typing import Any, Optional

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from .. import database as db_mod
from ..keyboards import (
    cancel_kb,
    channels_list_kb,
    main_menu,
    post_editor_kb,
    reactions_picker_kb,
)
from ..states import CreatePost
from ..utils import build_post_keyboard, parse_url_buttons, restore_entities


router = Router(name="nb2_post")


MEDIA_CONTENT_TYPES = {"photo", "video", "document", "audio", "animation", "voice", "video_note"}


def _empty_draft() -> dict[str, Any]:
    return {
        "channel_id": None,
        "channel_title": None,
        "content_type": "text",
        "file_id": None,
        "text": "",
        "entities": None,
        "url_buttons_raw": "",
        "reactions": [],
        "silent": False,
        "pin": False,
        "no_preview": False,
        "native_comments": True,
        "show_more": False,
        "preview_msg_id": None,
        "editor_msg_id": None,
    }


# ---------- Step 1: choose channel ----------

@router.message(F.text == "📝 Yangi post")
async def new_post(message: Message, state: FSMContext) -> None:
    channels = await db_mod.list_channels_for_user(message.from_user.id)
    if not channels:
        await message.answer(
            "Avval kanal qo'shing. «➕ Kanal qo'shish» tugmasini bosing.",
            reply_markup=main_menu(),
        )
        return
    await state.set_state(CreatePost.choosing_channel)
    await state.update_data(**_empty_draft())
    await message.answer(
        "📡 Qaysi kanalga post yuborasiz?",
        reply_markup=channels_list_kb(channels, action="pickch"),
    )


@router.callback_query(CreatePost.choosing_channel, F.data.startswith("pickch:"))
async def pick_channel(cb: CallbackQuery, state: FSMContext) -> None:
    chat_id = int(cb.data.split(":", 1)[1])
    ch = await db_mod.get_channel(chat_id)
    if not ch or not await db_mod.is_user_channel_admin(chat_id, cb.from_user.id):
        await cb.answer("Sizda bu kanalga huquq yo'q.", show_alert=True)
        return
    await state.update_data(channel_id=chat_id, channel_title=ch["title"])
    await state.set_state(CreatePost.composing)
    try:
        await cb.message.delete()
    except TelegramAPIError:
        pass
    await cb.message.answer(
        f"📝 <b>{ch['title']}</b> uchun postni yuboring.\n\n"
        f"Matn, rasm, video, hujjat, audio yoki GIF — istalganini yuborishingiz mumkin.",
        reply_markup=cancel_kb(),
    )
    await cb.answer()


# ---------- Step 2: receive content ----------

@router.message(CreatePost.composing, F.content_type.in_({
    "text", "photo", "video", "document", "audio", "animation", "voice", "video_note"
}))
async def receive_content(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()

    text = message.text or message.caption or ""
    entities = message.entities or message.caption_entities

    content_type = message.content_type
    file_id: Optional[str] = None
    if content_type == "photo" and message.photo:
        file_id = message.photo[-1].file_id
    elif content_type == "video" and message.video:
        file_id = message.video.file_id
    elif content_type == "document" and message.document:
        file_id = message.document.file_id
    elif content_type == "audio" and message.audio:
        file_id = message.audio.file_id
    elif content_type == "animation" and message.animation:
        file_id = message.animation.file_id
    elif content_type == "voice" and message.voice:
        file_id = message.voice.file_id
    elif content_type == "video_note" and message.video_note:
        file_id = message.video_note.file_id

    data["content_type"] = content_type
    data["file_id"] = file_id
    data["text"] = text
    data["entities"] = [e.model_dump(exclude_none=True) for e in entities] if entities else None
    await state.update_data(**data)

    await _render_preview(bot, message.chat.id, state)


# ---------- Preview rendering ----------

async def _render_preview(bot: Bot, chat_id: int, state: FSMContext) -> None:
    data = await state.get_data()

    for key in ("preview_msg_id", "editor_msg_id"):
        msg_id = data.get(key)
        if msg_id:
            try:
                await bot.delete_message(chat_id, msg_id)
            except TelegramAPIError:
                pass

    url_rows, url_errs = parse_url_buttons(data.get("url_buttons_raw") or "")
    reactions = data.get("reactions") or []
    preview_kb = build_post_keyboard(url_rows, reactions, post_id=None, counts={})

    user_text = data.get("text") or ""
    content_type = data.get("content_type", "text")
    file_id = data.get("file_id")
    entities = restore_entities(data.get("entities"))
    has_user_text = bool(user_text)

    sent: Message
    try:
        if content_type == "text" or not file_id:
            text_for_send = user_text or "<i>(matn yo'q)</i>"
            send_entities = entities if has_user_text else None
            send_pm = None if (has_user_text and send_entities) else "HTML"
            sent = await bot.send_message(
                chat_id, text_for_send, reply_markup=preview_kb,
                entities=send_entities,
                parse_mode=send_pm,
                disable_web_page_preview=data.get("no_preview", False),
            )
        elif content_type == "photo":
            sent = await bot.send_photo(chat_id, file_id, caption=user_text or None, caption_entities=entities, parse_mode=None, reply_markup=preview_kb)
        elif content_type == "video":
            sent = await bot.send_video(chat_id, file_id, caption=user_text or None, caption_entities=entities, parse_mode=None, reply_markup=preview_kb)
        elif content_type == "document":
            sent = await bot.send_document(chat_id, file_id, caption=user_text or None, caption_entities=entities, parse_mode=None, reply_markup=preview_kb)
        elif content_type == "audio":
            sent = await bot.send_audio(chat_id, file_id, caption=user_text or None, caption_entities=entities, parse_mode=None, reply_markup=preview_kb)
        elif content_type == "animation":
            sent = await bot.send_animation(chat_id, file_id, caption=user_text or None, caption_entities=entities, parse_mode=None, reply_markup=preview_kb)
        elif content_type == "voice":
            sent = await bot.send_voice(chat_id, file_id, caption=user_text or None, caption_entities=entities, parse_mode=None, reply_markup=preview_kb)
        elif content_type == "video_note":
            sent = await bot.send_video_note(chat_id, file_id, reply_markup=preview_kb)
        else:
            sent = await bot.send_message(chat_id, user_text, reply_markup=preview_kb, parse_mode=None, entities=entities)
    except TelegramAPIError as e:
        await bot.send_message(chat_id, f"❌ Old-ko'rinishni ko'rsata olmadim: {e}")
        return

    preview_id = sent.message_id

    has_buttons = bool(url_rows)
    has_reactions = bool(reactions)
    has_media = content_type != "text" and bool(file_id)

    status_lines = ["⚙️ <b>Post sozlamalari</b>"]
    status_lines.append(f"📡 Kanal: <b>{data.get('channel_title') or '—'}</b>")
    status_lines.append(f"📎 Media: {'bor' if has_media else 'yo`q'}")
    status_lines.append(f"🔗 Tugmalar: {len(url_rows)} qator")
    status_lines.append(f"👍 Reaksiyalar: {len(reactions)} ta")
    status_lines.append(f"🔕 Ovozsiz: {'ha' if data.get('silent') else 'yo`q'}")
    if data.get("pin"):
        status_lines.append("📌 Pin: ha")
    if data.get("no_preview"):
        status_lines.append("🚫 Old-ko'rinish: o'chirilgan")
    if url_errs:
        status_lines.append("⚠️ Tugmalardagi xatolar:")
        for e in url_errs[:5]:
            status_lines.append(f"  • {e}")

    editor = await bot.send_message(
        chat_id,
        "\n".join(status_lines),
        reply_markup=post_editor_kb(
            silent=data.get("silent", False),
            has_buttons=has_buttons,
            has_reactions=has_reactions,
            has_media=has_media,
            show_more=data.get("show_more", False),
        ),
    )

    await state.update_data(preview_msg_id=preview_id, editor_msg_id=editor.message_id)


# ---------- Editor callbacks ----------

@router.callback_query(F.data == "ed:more")
async def ed_more(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.update_data(show_more=True)
    await _render_preview(bot, cb.message.chat.id, state)
    await cb.answer()


@router.callback_query(F.data == "ed:less")
async def ed_less(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.update_data(show_more=False)
    await _render_preview(bot, cb.message.chat.id, state)
    await cb.answer()


@router.callback_query(F.data == "ed:silent")
async def ed_silent(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await state.update_data(silent=not data.get("silent", False))
    await _render_preview(bot, cb.message.chat.id, state)
    await cb.answer("🔕 O'zgartirildi")


@router.callback_query(F.data == "ed:pin")
async def ed_pin(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await state.update_data(pin=not data.get("pin", False))
    await _render_preview(bot, cb.message.chat.id, state)
    await cb.answer("📌 O'zgartirildi")


@router.callback_query(F.data == "ed:nopreview")
async def ed_nopreview(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await state.update_data(no_preview=not data.get("no_preview", False))
    await _render_preview(bot, cb.message.chat.id, state)
    await cb.answer("Old-ko'rinish o'zgartirildi")


@router.callback_query(F.data == "ed:discard")
async def ed_discard(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    for key in ("preview_msg_id", "editor_msg_id"):
        msg_id = data.get(key)
        if msg_id:
            try:
                await bot.delete_message(cb.message.chat.id, msg_id)
            except TelegramAPIError:
                pass
    await state.clear()
    await cb.message.answer("🗑 Post o'chirildi. Yangi post uchun «📝 Yangi post» tugmasini bosing.", reply_markup=main_menu())
    await cb.answer()


@router.callback_query(F.data == "ed:cancel")
async def ed_cancel(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await ed_discard(cb, state, bot)


@router.callback_query(F.data == "ed:comments")
async def ed_comments(cb: CallbackQuery) -> None:
    await cb.answer(
        "💬 Izohlar (comments) kanalingizga Discussion Group ulanganda avtomatik "
        "ishlaydi. Kanal sozlamalari → Discussion → guruh tanlang.",
        show_alert=True,
    )


@router.callback_query(F.data == "ed:native_comments")
async def ed_native_comments(cb: CallbackQuery) -> None:
    await cb.answer(
        "ℹ️ Native Comments — bu Telegramning o'rnatilgan izohlar tizimi. "
        "Faqat kanalda Discussion Group ulangan bo'lsa ishlaydi.",
        show_alert=True,
    )


# ---------- Media (re)attach ----------

@router.callback_query(F.data == "ed:media")
async def ed_media(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CreatePost.adding_media)
    await cb.message.answer(
        "📎 Yangi mediafayl yuboring (rasm/video/hujjat/audio/GIF/voice).\n"
        "Yoki <b>matn</b> yuboring — joriy media olib tashlanadi.",
        reply_markup=cancel_kb(),
    )
    await cb.answer()


@router.message(CreatePost.adding_media, F.content_type.in_({
    "text", "photo", "video", "document", "audio", "animation", "voice", "video_note"
}))
async def receive_new_media(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    content_type = message.content_type
    text_old = data.get("text") or ""
    new_text = message.text or message.caption
    entities = message.entities or message.caption_entities

    file_id: Optional[str] = None
    if content_type == "photo" and message.photo:
        file_id = message.photo[-1].file_id
    elif content_type == "video" and message.video:
        file_id = message.video.file_id
    elif content_type == "document" and message.document:
        file_id = message.document.file_id
    elif content_type == "audio" and message.audio:
        file_id = message.audio.file_id
    elif content_type == "animation" and message.animation:
        file_id = message.animation.file_id
    elif content_type == "voice" and message.voice:
        file_id = message.voice.file_id
    elif content_type == "video_note" and message.video_note:
        file_id = message.video_note.file_id

    data["content_type"] = content_type
    data["file_id"] = file_id
    if new_text is not None:
        data["text"] = new_text
        data["entities"] = [e.model_dump(exclude_none=True) for e in entities] if entities else None
    elif content_type == "text":
        data["text"] = text_old
    await state.update_data(**data)
    await state.set_state(CreatePost.composing)
    await _render_preview(bot, message.chat.id, state)


# ---------- URL buttons ----------

@router.callback_query(F.data == "ed:buttons")
async def ed_buttons(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CreatePost.editing_buttons)
    await cb.message.answer(
        "🔗 <b>URL-tugmalar</b>\n\n"
        "Har bir qatorga bitta tugma yozing. Format:\n"
        "<code>Matn - URL</code>\n\n"
        "Bir qatorda bir nechta tugma uchun <code>|</code> bilan ajrating:\n"
        "<code>Sayt - https://nuriddinbuildings.uz</code>\n"
        "<code>IG - https://instagram.com/x | TG - @kanal</code>\n\n"
        "Tugmalarni olib tashlash uchun <code>-</code> (bitta tire) yuboring.",
        reply_markup=cancel_kb(),
    )
    await cb.answer()


@router.message(CreatePost.editing_buttons, F.text)
async def receive_buttons(message: Message, state: FSMContext, bot: Bot) -> None:
    raw = message.text.strip()
    if raw == "-":
        raw = ""
    await state.update_data(url_buttons_raw=raw)
    await state.set_state(CreatePost.composing)
    await _render_preview(bot, message.chat.id, state)


# ---------- Reactions ----------

@router.callback_query(F.data == "ed:reactions")
async def ed_reactions(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(CreatePost.editing_reactions)
    await cb.message.answer(
        "👍 <b>Reaksiyalarni tanlang</b>\n\n"
        "Postda chiqishi kerak bo'lgan reaksiya tugmalarini belgilang.",
        reply_markup=reactions_picker_kb(data.get("reactions") or []),
    )
    await cb.answer()


@router.callback_query(CreatePost.editing_reactions, F.data.startswith("rxpick:"))
async def reactions_pick(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    action = cb.data.split(":", 1)[1]
    data = await state.get_data()
    reactions = list(data.get("reactions") or [])

    if action == "clear":
        reactions = []
        await state.update_data(reactions=reactions)
        await cb.message.edit_reply_markup(reply_markup=reactions_picker_kb(reactions))
        await cb.answer("Tozalandi")
        return
    if action == "done":
        try:
            await cb.message.delete()
        except TelegramAPIError:
            pass
        await state.set_state(CreatePost.composing)
        await _render_preview(bot, cb.message.chat.id, state)
        await cb.answer("✅ Saqlandi")
        return

    emoji = action
    if emoji in reactions:
        reactions.remove(emoji)
    else:
        if len(reactions) >= 8:
            await cb.answer("Maksimum 8 ta reaksiya", show_alert=True)
            return
        reactions.append(emoji)
    await state.update_data(reactions=reactions)
    try:
        await cb.message.edit_reply_markup(reply_markup=reactions_picker_kb(reactions))
    except TelegramAPIError:
        pass
    await cb.answer()


# ---------- Publish ----------

@router.callback_query(F.data == "ed:publish")
async def ed_publish(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    chat_id = data.get("channel_id")
    if not chat_id:
        await cb.answer("Kanal tanlanmagan", show_alert=True)
        return

    text = data.get("text") or ""
    content_type = data.get("content_type", "text")
    file_id = data.get("file_id")
    silent = bool(data.get("silent"))
    no_preview = bool(data.get("no_preview"))
    entities = restore_entities(data.get("entities"))

    url_rows, _ = parse_url_buttons(data.get("url_buttons_raw") or "")
    reactions = data.get("reactions") or []

    kb_no_pid = build_post_keyboard(url_rows, reactions, post_id=None, counts={})

    try:
        if content_type == "text" or not file_id:
            sent = await bot.send_message(
                chat_id, text, reply_markup=kb_no_pid,
                entities=entities, parse_mode=None,
                disable_notification=silent,
                disable_web_page_preview=no_preview,
            )
        elif content_type == "photo":
            sent = await bot.send_photo(chat_id, file_id, caption=text or None, caption_entities=entities, parse_mode=None, reply_markup=kb_no_pid, disable_notification=silent)
        elif content_type == "video":
            sent = await bot.send_video(chat_id, file_id, caption=text or None, caption_entities=entities, parse_mode=None, reply_markup=kb_no_pid, disable_notification=silent)
        elif content_type == "document":
            sent = await bot.send_document(chat_id, file_id, caption=text or None, caption_entities=entities, parse_mode=None, reply_markup=kb_no_pid, disable_notification=silent)
        elif content_type == "audio":
            sent = await bot.send_audio(chat_id, file_id, caption=text or None, caption_entities=entities, parse_mode=None, reply_markup=kb_no_pid, disable_notification=silent)
        elif content_type == "animation":
            sent = await bot.send_animation(chat_id, file_id, caption=text or None, caption_entities=entities, parse_mode=None, reply_markup=kb_no_pid, disable_notification=silent)
        elif content_type == "voice":
            sent = await bot.send_voice(chat_id, file_id, caption=text or None, caption_entities=entities, parse_mode=None, reply_markup=kb_no_pid, disable_notification=silent)
        elif content_type == "video_note":
            sent = await bot.send_video_note(chat_id, file_id, reply_markup=kb_no_pid, disable_notification=silent)
        else:
            sent = await bot.send_message(chat_id, text, reply_markup=kb_no_pid, parse_mode=None, entities=entities, disable_notification=silent)
    except TelegramAPIError as e:
        await cb.answer(f"❌ Yuborib bo'lmadi: {e}", show_alert=True)
        return

    if reactions:
        post_id = await db_mod.create_post(chat_id, sent.message_id, cb.from_user.id, reactions)
        kb = build_post_keyboard(url_rows, reactions, post_id=post_id, counts={})
        try:
            await bot.edit_message_reply_markup(chat_id, sent.message_id, reply_markup=kb)
        except TelegramAPIError:
            pass

    if data.get("pin"):
        try:
            await bot.pin_chat_message(chat_id, sent.message_id, disable_notification=silent)
        except TelegramAPIError:
            pass

    for key in ("preview_msg_id", "editor_msg_id"):
        msg_id = data.get(key)
        if msg_id:
            try:
                await bot.delete_message(cb.message.chat.id, msg_id)
            except TelegramAPIError:
                pass

    await state.clear()
    link = _post_link(chat_id, sent.message_id, data.get("channel_title"))
    await cb.message.answer(
        f"✅ Post nashr etildi!\n{link}",
        reply_markup=main_menu(),
        disable_web_page_preview=True,
    )
    await cb.answer("Yuborildi ✅")


def _post_link(chat_id: int, message_id: int, title: Optional[str]) -> str:
    if chat_id < 0:
        short = str(chat_id).removeprefix("-100")
        return f"🔗 https://t.me/c/{short}/{message_id}"
    return f"🔗 (kanal: {title or chat_id})"
