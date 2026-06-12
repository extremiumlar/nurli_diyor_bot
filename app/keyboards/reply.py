from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def client_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏢 Bizning Proyektlar")],
            [KeyboardButton(text="📊 Loyiha Bosqichlari")],
            [KeyboardButton(text="🔔 Yangiliklarga Obuna")],
            [KeyboardButton(text="📞 Bog'lanish")],
            [KeyboardButton(text="🔄 Rolni o'zgartirish")],
        ],
        resize_keyboard=True
    )


def jobseeker_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Mavjud Vakansiyalar")],
            [KeyboardButton(text="📝 Ariza Topshirish")],
            [KeyboardButton(text="🔄 Rolni o'zgartirish")],
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
