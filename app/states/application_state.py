from aiogram.fsm.state import State, StatesGroup


class ApplicationState(StatesGroup):
    # Foydalanuvchidan tartibli ravishda so'raladigan savollar
    consent           = State()   # 0. Boshlang'ich rozilik (Ha/Yo'q)
    full_name         = State()   # 1. Ism-familiyasi
    phone             = State()   # 2. Telefon raqami
    age               = State()   # 3. Yosh
    address           = State()   # 4. Qayerdan
    languages         = State()   # 5. Qaysi tillarni biladi
    vacancy           = State()   # 6. Qanday kasbda ishlamoqchi (lavozim)
    past_work         = State()   # 7. Qayerda ishlagan
    education         = State()   # 8. Ma'lumoti
    additional_skills = State()   # 9. Qo'shimcha bilim va ko'nikmalar
    photo             = State()   # 10. Rasm
    expected_salary   = State()   # 11. Kutgan oylik maosh


class ScreeningState(StatesGroup):
    """2- va 3-bosqich: test, yozma savollar va video."""
    test    = State()   # test savollari (joriy index FSM data'da: t_idx)
    written = State()   # yozma savollar (joriy index FSM data'da: w_idx)
    video   = State()   # video-vizitka


class HRScoreState(StatesGroup):
    """HR yozma javob va videoni qo'lda baholaydi."""
    written_score = State()   # yozma javobga ball (app_id, order FSM data'da)
    video_score   = State()   # videoga 0–4 ball
