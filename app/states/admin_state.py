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
    schedule     = State()


class BroadcastState(StatesGroup):
    segment = State()
    message = State()
    confirm = State()


class AddAdminState(StatesGroup):
    telegram_id = State()   # admin Telegram ID si
    role        = State()   # rol tanlash


class EditAdminState(StatesGroup):
    role = State()          # yangi rol tanlash
