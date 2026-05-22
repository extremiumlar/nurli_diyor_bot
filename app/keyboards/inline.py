from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def role_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Men mijozman",
                    callback_data="role:client"
                ),
                InlineKeyboardButton(
                    text="👷 Ish qidiraman",
                    callback_data="role:jobseeker"
                )
            ]
        ]
    )

def subscribe_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Kanalga obuna bo‘lish",
                    url="https://t.me/YOUR_CHANNEL_USERNAME"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Obuna bo‘ldim",
                    callback_data="check_subscribe"
                )
            ]
        ]
    )