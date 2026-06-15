from aiogram.fsm.state import State, StatesGroup


class AddChannel(StatesGroup):
    waiting_forward = State()


class CreatePost(StatesGroup):
    choosing_channel = State()
    composing = State()
    editing_buttons = State()
    editing_reactions = State()
    adding_media = State()
