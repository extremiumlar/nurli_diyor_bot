from aiogram.fsm.state import State, StatesGroup


class ApplicationState(StatesGroup):
    # Foydalanuvchidan tartibli ravishda so'raladigan savollar
    full_name         = State()   # 1. Ism-familiyasi
    phone             = State()   # 2. Telefon raqami
    age               = State()   # 3. Yosh
    address           = State()   # 4. Qayerdan
    languages         = State()   # 5. Qaysi tillarni biladi
    vacancy           = State()   # 6. Qanday kasbda ishlamoqchi (lavozim)
    past_work         = State()   # 7. Qayerda ishlagan
    education         = State()   # 8. Ma'lumoti
    additional_skills = State()   # 9. Qo'shimcha bilim va ko'nikmalar
