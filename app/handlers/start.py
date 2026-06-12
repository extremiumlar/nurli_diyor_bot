from aiogram import Router, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from app.config import CHANNEL_ID, CHANNEL_LINK, INSTAGRAM_URL
from app.database.crud import create_or_update_user, update_user_role, get_user
from app.keyboards.inline import (
    subscribe_keyboard, not_subscribed_keyboard,
    role_keyboard, change_role_keyboard
)
from app.keyboards.reply import client_menu, jobseeker_menu

router = Router()

# ── Matnlar ────────────────────────────────────────────────────────────────

def _subscribe_text() -> str:
    has_instagram = bool(INSTAGRAM_URL)
    lines = [
        "👋 <b>Qurilish kompaniyasi botiga xush kelibsiz!</b>\n",
        "Botdan foydalanish uchun quyidagilarga obuna bo'ling:\n",
        "📢 <b>Telegram kanal</b> — yangiliklar va loyihalar",
    ]
    if has_instagram:
        lines.append("📸 <b>Instagram</b> — foto va videolar")
    lines.append('\nObuna bo\'lgach <b>"✅ Obuna bo\'ldim"</b> tugmasini bosing.')
    return "\n".join(lines)


NOT_SUBSCRIBED_TEXT = (
    "❌ <b>Telegram kanalga obuna topilmadi!</b>\n\n"
    "Iltimos, avval kanalga obuna bo'ling va qayta tekshiring."
)

ROLE_NAMES = {"client": "👤 Mijoz", "jobseeker": "👷 Ish izlovchi"}


# ── Yordamchi funksiyalar ──────────────────────────────────────────────────

async def check_channel_subscription(bot: Bot, user_id: int) -> bool:
    if not CHANNEL_ID:
        return True   # .env da CHANNEL_ID yo'q — tekshiruvsiz o'tkazish
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except TelegramBadRequest as e:
        # Ko'p hollarda: bot kanal administratori emas
        print(f"[KANAL XATOSI] TelegramBadRequest: {e}")
        return False
    except Exception as e:
        print(f"[KANAL XATOSI] {type(e).__name__}: {e}")
        return False


async def send_subscribe_prompt(message: Message):
    await message.answer(
        _subscribe_text(),
        parse_mode="HTML",
        reply_markup=subscribe_keyboard(CHANNEL_LINK, INSTAGRAM_URL)
    )


def _menu_for_role(role: str):
    return client_menu() if role == "client" else jobseeker_menu()


# ── /start ─────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot):
    is_sub = await check_channel_subscription(bot, message.from_user.id)
    if not is_sub:
        await send_subscribe_prompt(message)
        return

    user = await create_or_update_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name
    )

    if user.role in ("client", "jobseeker"):
        await message.answer(
            f"Xush kelibsiz! {ROLE_NAMES[user.role]} menyusi:",
            reply_markup=_menu_for_role(user.role)
        )
    else:
        await message.answer(
            "👋 <b>Qurilish kompaniyasi botiga xush kelibsiz!</b>\n\nRolingizni tanlang:",
            parse_mode="HTML",
            reply_markup=role_keyboard()
        )


# ── Obuna tekshiruvi ───────────────────────────────────────────────────────

@router.callback_query(lambda c: c.data == "check_subscribe")
async def check_subscribe_callback(callback: CallbackQuery, bot: Bot):
    is_sub = await check_channel_subscription(bot, callback.from_user.id)

    if not is_sub:
        await callback.answer("Kanalga obuna topilmadi! Iltimos obuna bo'ling.", show_alert=True)
        await callback.message.edit_text(
            NOT_SUBSCRIBED_TEXT,
            parse_mode="HTML",
            reply_markup=not_subscribed_keyboard(CHANNEL_LINK, INSTAGRAM_URL)
        )
        return

    await callback.message.delete()

    user = await create_or_update_user(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name
    )

    if user.role in ("client", "jobseeker"):
        await callback.message.answer(
            f"✅ Obuna tasdiqlandi! {ROLE_NAMES[user.role]} menyusi:",
            reply_markup=_menu_for_role(user.role)
        )
    else:
        await callback.message.answer(
            "✅ <b>Obuna tasdiqlandi!</b>\n\nRolingizni tanlang:",
            parse_mode="HTML",
            reply_markup=role_keyboard()
        )
    await callback.answer()


# ── 🔄 Rolni o'zgartirish (reply tugma) ───────────────────────────────────

@router.message(F.text == "🔄 Rolni o'zgartirish")
async def change_role_handler(message: Message, state: FSMContext):
    # Agar FSM oqimida bo'lsa — bekor qilamiz
    await state.clear()

    user = await get_user(message.from_user.id)
    current_role = user.role if user else None

    if current_role in ("client", "jobseeker"):
        current_label = ROLE_NAMES[current_role]
        text = (
            f"Hozirgi rolingiz: <b>{current_label}</b>\n\n"
            "Qaysi rolga o'tmoqchisiz?"
        )
    else:
        text = "Rolingizni tanlang:"

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=change_role_keyboard(current_role or "")
    )


# ── Rol tanlash / o'zgartirish (callback) ─────────────────────────────────

@router.callback_query(lambda c: c.data.startswith("role:"))
async def role_callback(callback: CallbackQuery):
    new_role = callback.data.split(":")[1]
    user = await get_user(callback.from_user.id)
    old_role = user.role if user else None

    await update_user_role(callback.from_user.id, new_role)

    # Xabarni o'chirish (rol tanlash xabari)
    try:
        await callback.message.delete()
    except Exception:
        pass

    if new_role == old_role:
        # Xuddi shu rol qayta tanlandi
        await callback.message.answer(
            f"Siz allaqachon {ROLE_NAMES[new_role]} sifatida ro'yxatdansiz.",
            reply_markup=_menu_for_role(new_role)
        )
    else:
        action = "ro'yxatdan o'tdingiz" if not old_role else "o'tdingiz"
        await callback.message.answer(
            f"✅ <b>{ROLE_NAMES[new_role]}</b> sifatida {action}!",
            parse_mode="HTML",
            reply_markup=_menu_for_role(new_role)
        )

    await callback.answer()
