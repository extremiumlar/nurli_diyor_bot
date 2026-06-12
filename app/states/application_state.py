from aiogram.fsm.state import State, StatesGroup


class ApplicationState(StatesGroup):
    # --- Umumiy savollar (barcha lavozimlar uchun) ---
    full_name  = State()   # 1. Ismi-familiyasi
    phone      = State()   # 2. Telefon raqami
    address    = State()   # 3. Yashash manzili
    birthday = State()   # 4. Tug'ilgan yili
    education  = State()   # 5. Ma'lumoti (o'rta, oliy, ...)
    # --- Lavozimga oid ---
    vacancy    = State()   # 6. Qaysi lavozim (agar oldin tanlanmagan bo'lsa)
    experience = State()   # 7. Ish staji
    cv         = State()   # 8. CV fayl
