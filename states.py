from aiogram.fsm.state import State, StatesGroup


class Profile(StatesGroup):
    sex = State()
    name = State()
    age = State()
    weight = State()
    height = State()
    city = State()
    target = State()
    confirm_target = State()
    confirm_delete = State()


class LogWaterStates(StatesGroup):
    water_volume = State()


class LogFoodStates(StatesGroup):
    name_food = State()
    food_weight = State()
    food_ccal = State()