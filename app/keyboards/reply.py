from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏢 Bizning Proyektlar")],
            [KeyboardButton(text="📊 Loyiha Bosqichlari")],
            [KeyboardButton(text="🔔 Yangiliklarga Obuna")],
            [KeyboardButton(text="📞 Bog‘lanish")]
        ],
        resize_keyboard=True
    )

def jobseeker_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Mavjud Vakansiyalar")],
            [KeyboardButton(text="📝 Ariza Topshirish")]
        ],
        resize_keyboard=True
    )