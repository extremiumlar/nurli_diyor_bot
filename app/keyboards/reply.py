from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    """Asosiy menyu — barcha foydalanuvchilar uchun."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Mavjud Vakansiyalar")],
            [KeyboardButton(text="📝 Ariza Topshirish")],
        ],
        resize_keyboard=True
    )


def phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def remove_keyboard():
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()
