from aiogram.fsm.state import State, StatesGroup

class Profile(StatesGroup):
    sex = State()
    name = State()
    age = State()
    weight = State()
    height = State()
    city = State()
    cnt_active_min_for_day = State()
    target = State()
    confirm_target = State()
    confirm_delete = State()