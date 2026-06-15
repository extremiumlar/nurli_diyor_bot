from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ChatMemberAdministrator, ChatMemberOwner, Message

from .. import database as db_mod
from ..keyboards import cancel_kb, channel_actions_kb, channels_list_kb, main_menu
from ..states import AddChannel


router = Router(name="nb2_channels")


ADD_PROMPT = (
    "🧩 <b>Kanal qo'shish</b>\n\n"
    "1. Botni kanalingizga <b>admin</b> qilib qo'shing (post yuborish ruxsati bilan).\n"
    "2. Keyin shu kanalingizdan istalgan postni botga <b>forward</b> qiling.\n\n"
    "Bekor qilish uchun «❌ Bekor qilish» tugmasini bosing."
)


@router.message(F.text == "➕ Kanal qo'shish")
async def add_channel_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AddChannel.waiting_forward)
    await message.answer(ADD_PROMPT, reply_markup=cancel_kb())


@router.message(AddChannel.waiting_forward, F.forward_from_chat)
async def add_channel_forward(message: Message, state: FSMContext, bot: Bot) -> None:
    fwd = message.forward_from_chat
    if not fwd or fwd.type != "channel":
        await message.answer("⚠️ Bu kanal posti emas. Iltimos, kanal postini forward qiling.")
        return

    chat_id = fwd.id
    title = fwd.title or "Kanal"
    username = fwd.username
    user_id = message.from_user.id

    try:
        me = await bot.get_me()
        bot_member = await bot.get_chat_member(chat_id, me.id)
    except TelegramAPIError:
        await message.answer(
            "❌ Botni kanalda ko'ra olmayapman. Iltimos, avval botni kanalga "
            "<b>admin</b> qilib qo'shing va qaytadan urinib ko'ring.",
            reply_markup=main_menu(),
        )
        await state.clear()
        return

    if not isinstance(bot_member, (ChatMemberAdministrator, ChatMemberOwner)):
        await message.answer(
            "❌ Bot kanalda admin emas. Iltimos, botni admin qiling "
            "(<b>Post yuborish</b> huquqi bilan) va qaytadan urinib ko'ring.",
            reply_markup=main_menu(),
        )
        await state.clear()
        return

    if isinstance(bot_member, ChatMemberAdministrator) and not bot_member.can_post_messages:
        await message.answer(
            "❌ Botda «Post yuborish» huquqi yo'q. Kanal sozlamalaridan ushbu "
            "huquqni bering va qayta urinib ko'ring.",
            reply_markup=main_menu(),
        )
        await state.clear()
        return

    try:
        user_member = await bot.get_chat_member(chat_id, user_id)
    except TelegramAPIError:
        await message.answer("❌ Sizning a'zoligingizni tekshira olmadim.", reply_markup=main_menu())
        await state.clear()
        return

    if not isinstance(user_member, (ChatMemberAdministrator, ChatMemberOwner)):
        await message.answer(
            "❌ Siz bu kanalda admin emassiz. Faqat kanal adminlari kanal qo'sha oladi.",
            reply_markup=main_menu(),
        )
        await state.clear()
        return

    await db_mod.upsert_channel(chat_id, title, username, added_by=user_id)
    admin_ids = await _fetch_admin_ids(bot, chat_id)
    await db_mod.set_channel_admins(chat_id, admin_ids)

    await message.answer(
        f"✅ Kanal qo'shildi: <b>{title}</b>\n\n"
        f"Endi «📝 Yangi post» tugmasini bosib post yarata olasiz.",
        reply_markup=main_menu(),
    )
    await state.clear()


@router.message(AddChannel.waiting_forward)
async def add_channel_wrong(message: Message) -> None:
    await message.answer("⚠️ Iltimos, kanal postini forward qiling yoki bekor qiling.")


@router.message(F.text == "📡 Mening kanallarim")
async def list_channels(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id
    channels = await db_mod.list_channels_for_user(user_id)
    if not channels:
        await message.answer(
            "Sizning kanallaringiz yo'q.\n\n«➕ Kanal qo'shish» tugmasini bosib boshlang.",
            reply_markup=main_menu(),
        )
        return

    await message.answer(
        "📡 <b>Kanallaringiz:</b>\nBoshqarish uchun kanalni tanlang.",
        reply_markup=channels_list_kb(channels, action="chinfo"),
    )


@router.callback_query(F.data.startswith("chinfo:"))
async def channel_info(cb: CallbackQuery) -> None:
    chat_id = int(cb.data.split(":", 1)[1])
    ch = await db_mod.get_channel(chat_id)
    if not ch:
        await cb.answer("Kanal topilmadi", show_alert=True)
        return
    text = f"📡 <b>{ch['title']}</b>"
    if ch["username"]:
        text += f"\n@{ch['username']}"
    await cb.message.edit_text(text, reply_markup=channel_actions_kb(chat_id))
    await cb.answer()


@router.callback_query(F.data == "chback")
async def channel_back(cb: CallbackQuery) -> None:
    user_id = cb.from_user.id
    channels = await db_mod.list_channels_for_user(user_id)
    if not channels:
        await cb.message.edit_text("Sizning kanallaringiz yo'q.")
        await cb.answer()
        return
    await cb.message.edit_text(
        "📡 <b>Kanallaringiz:</b>\nBoshqarish uchun kanalni tanlang.",
        reply_markup=channels_list_kb(channels, action="chinfo"),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("chdel:"))
async def channel_delete(cb: CallbackQuery) -> None:
    chat_id = int(cb.data.split(":", 1)[1])
    if not await db_mod.is_user_channel_admin(chat_id, cb.from_user.id):
        await cb.answer("Sizda ruxsat yo'q", show_alert=True)
        return
    await db_mod.remove_channel(chat_id)
    await cb.message.edit_text("✅ Kanal ro'yxatdan olib tashlandi.")
    await cb.answer()


async def _fetch_admin_ids(bot: Bot, chat_id: int) -> list[int]:
    try:
        admins = await bot.get_chat_administrators(chat_id)
    except TelegramAPIError:
        return []
    return [a.user.id for a in admins if not a.user.is_bot]


async def refresh_admins_for_user(bot: Bot, user_id: int) -> None:
    async with db_mod.db().execute("SELECT chat_id FROM channels") as cur:
        rows = await cur.fetchall()
    for row in rows:
        chat_id = row["chat_id"]
        admin_ids = await _fetch_admin_ids(bot, chat_id)
        if admin_ids:
            await db_mod.set_channel_admins(chat_id, admin_ids)
