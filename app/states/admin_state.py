from aiogram.fsm.state import State, StatesGroup


class AddProjectState(StatesGroup):
    name        = State()
    address     = State()
    description = State()
    photos      = State()


class AddStageState(StatesGroup):
    project = State()
    name    = State()


class UpdateStagePhotoState(StatesGroup):
    project = State()
    stage   = State()
    photo   = State()
    note    = State()


class AddVacancyState(StatesGroup):
    title        = State()
    requirements = State()
    salary       = State()


class BroadcastState(StatesGroup):
    segment = State()
    message = State()
    confirm = State()


class AnnounceState(StatesGroup):
    picking = State()   # vakansiya bo'yicha filtr uchun ko'p tanlash


class QuestionEditState(StatesGroup):
    """Admin savollarni qo'lda yaratish/tahrirlash."""
    review      = State()   # AI yaratgan to'plamni ko'rib chiqish
    q_text      = State()   # savol matnini o'zgartirish
    opt_text    = State()   # test variant matnini o'zgartirish
    new_test_q  = State()   # yangi test savoli: matn
    new_test_o3 = State()   # yangi test savoli: 3 ballik javob
    new_test_o1 = State()   # yangi test savoli: 1 ballik javob
    new_test_o0 = State()   # yangi test savoli: 0 ballik javob
    new_written = State()   # yangi yozma savol
    new_video   = State()   # video-savol matni


class AddAdminState(StatesGroup):
    telegram_id = State()   # admin Telegram ID si
    role        = State()   # rol tanlash


class EditAdminState(StatesGroup):
    role = State()


class EditVacancyState(StatesGroup):
    field = State()
    value = State()


class BotSettingsState(StatesGroup):
    channel   = State()
    instagram = State()


class SearchApplicationState(StatesGroup):
    tartib = State()


class ContactApplicantState(StatesGroup):
    message = State()
