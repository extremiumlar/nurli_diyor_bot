from aiogram.fsm.state import State, StatesGroup


class LeadState(StatesGroup):
    full_name = State()
    phone = State()
    project = State()
    note = State()
