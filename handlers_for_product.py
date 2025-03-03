from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from datetime import datetime
import pytz


from states import LogWaterStates, LogFoodStates
from work_with_json_file import log_water, log_food
from get_ccal_for_product import get_food_info


router2 = Router()


async def process_invalid_value(message: Message, prompt: str):
    await message.reply(prompt)


@router2.message(Command("log_water"))
async def cmd_log_water(message: Message, state: FSMContext):
    await message.reply("Введите объем выпитой воды в миллилитрах")
    await state.set_state(LogWaterStates.water_volume)


@router2.message(LogWaterStates.water_volume, F.text.regexp(r'^\d+(\.\d+)?$'))
async def handle_water_input(message: Message, state: FSMContext):
    input_water = float(message.text)

    if input_water < 0:
        await process_invalid_value(message, ("Отрицательное число выпитой воды - это рвота?\n\nЕсли вы ошиблись при вводе, то введите объем выпитой воды в миллилитрах"))
    elif input_water == 0:
        await process_invalid_value(message, ("Спасибо что сообщили, что не выпили воду\n\nЕсли вы ошиблись при вводе, то введите объем выпитой воды в миллилитрах"))
    elif input_water > 5000:
        await process_invalid_value(message, ("Вы выпили близкую к смертельной дозу воды\nСрочно извергайте все обратно и обратитесь к врачу\n\nЕсли вы ошиблись при вводе, то введите объем выпитой воды в миллилитрах"))
    else:
        await state.update_data(water_volume=input_water)
        timezone = pytz.timezone("Europe/Moscow")
        current_datetime = datetime.now(timezone)
        current_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        user_id = str(message.from_user.id)
        await log_water(user_id, input_water)
        await message.answer(f"Вы выпили {input_water} миллилитров воды в {current_datetime} по Москве. Событие записано")
        await state.clear()
        await message.reply("Введите /help для вызова всех команд")


@router2.message(LogWaterStates.water_volume)
async def process_invalid_input_water(message: Message):
    await message.reply("Пожалуйста, введите объем выпитой воды в миллилитрах в виде числа в диапазоне [1, 5000]")


@router2.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext):
    await message.reply("Введите название съеденного продукта")
    await state.set_state(LogFoodStates.name_food)


@router2.message(LogFoodStates.name_food, F.text.regexp(r'^[a-zA-Zа-яА-ЯёЁ\s]+$'))
async def handle_food_name_input(message: Message, state: FSMContext):
    input_name_food = message.text
    food_data_from_API = await get_food_info(input_name_food)
    if food_data_from_API is None:
        await process_invalid_value(message, ("Сервис получения калорий недоступен, повторите операцию позже"))
    elif food_data_from_API == "Продукт не найден":
        await process_invalid_value(message, ("Сервис получения калорий не нашел продукт с таким названием\n\nПопробуйте ввести его название еще раз"))
    else:
        name = food_data_from_API.get('name', 'Неизвестно')
        calories = food_data_from_API.get('calories', 0)
        print("Получена калорийность продукта")

        if name == "Неизвестно" or calories == 0:
            await process_invalid_value(message, ("Сервису получения калорий не известен данный продукт\nЛибо не известная его калорийность\n\nПожалуйста, попробуйте ввести название продукта еще раз"))
        else:
            await state.update_data(name_food=input_name_food)
            print("Название продукта записано")
            await state.update_data(food_ccal=calories)
            print("Калорийность продукта записана")
            await message.reply("Введите количество съеденного продукта в граммах")
            await state.set_state(LogFoodStates.food_weight)


@router2.message(LogFoodStates.name_food)
async def process_invalid_input_food_name(message: Message):
    await message.reply("Пожалуйста, введите название съеденного продукта")


@router2.message(LogFoodStates.food_weight, F.text.regexp(r'^\d+(\.\d+)?$'))
async def handle_food_weight_input(message: Message, state: FSMContext):
    input_food_weight = float(message.text)

    if input_food_weight < 0:
        await process_invalid_value(message, ("Количество сьеденной еды не может быть отрицательным"))
    elif input_food_weight > 3000:
        await process_invalid_value(message, ("Вы обожралися, и можете взорваться\n\nЕсли вы ошиблись при вводе, то введите массу съеденной пищи в граммах "))
    else:
        await state.update_data(food_weight=input_food_weight)

        await save_food_log(message, state)
        await message.answer("Введите /help для вызова всех команд")


@router2.message(LogFoodStates.food_weight)
async def process_invalid_input_food_weight(message: Message):
    await message.reply("Пожалуйста, введите массу съеденного продукта в граммах")


async def save_food_log(message: Message, state: FSMContext):
    data = await state.get_data()
    name_food = data.get("name_food")
    food_ccal_for_100g = data.get("food_ccal")
    food_weight = data.get("food_weight")

    timezone = pytz.timezone("Europe/Moscow")
    current_datetime = datetime.now(timezone)
    current_datetime_str  = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    user_id = str(message.from_user.id)

    await log_food(user_id, name_food, food_weight, food_ccal_for_100g)
    await message.reply(
        f"Вы съели {food_weight} грамм {name_food} в {current_datetime_str} по Москве. Событие записано."
    )
    await state.clear()


