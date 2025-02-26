from aiogram.fsm.state import State, StatesGroup

class Profile(StatesGroup):
    sex = State()
    name = State()
    age = State()
    weight = State()
    #city = State()