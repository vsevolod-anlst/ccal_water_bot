from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from datetime import datetime
import pytz



from states import LogWaterStates, LogFoodStates, LogActivityStates
from work_with_json_file import log_water, log_food, log_activity
from get_ccal_for_product import get_food_info
from ccal_for_active import get_activity_value



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



@router2.message(Command("log_activity"))
async def cmd_log_activity(message: Message, state: FSMContext):
    await message.reply("Введите название активности которой вы занимались")
    await state.set_state(LogActivityStates.name_activity)



@router2.message(LogActivityStates.name_activity, F.text.regexp(r'^[а-яА-ЯёЁ]+(-[а-яА-ЯёЁ]+)*(\s[а-яА-ЯёЁ]+(-[а-яА-ЯёЁ]+)*)*$'))
async def handle_name_activity(message: Message, state: FSMContext):
    input_name_activity = message.text

    try:
        calories_for_activity = await get_activity_value(input_name_activity)
        print(f"Количество сжигаемых калорий для активности '{input_name_activity}': {calories_for_activity}")
        await state.update_data(name_activity=input_name_activity)
        await state.update_data(ccal_in_hour_for_activity=calories_for_activity)
        await message.reply("Введите длительность вашей активности в минутах")
        await state.set_state(LogActivityStates.time_activity)
    except ValueError as e:
        await message.answer(str(e))



@router2.message(LogActivityStates.name_activity)
async def process_invalid_input_name_activity(message: Message):
    await message.reply("Пожалуйста, название активности которой вы занимались на русском языке без цифр и спец символов")



@router2.message(LogActivityStates.time_activity, F.text.regexp(r'^\d+(\.\d+)?$'))
async def handle_time_activity(message: Message, state: FSMContext):
    input_time_activity = float(message.text)

    if input_time_activity < 0:
        await process_invalid_value(message, ("Время не может быть отрицательным или нулевым\n\nЕсли вы ошиблись при вводе, то введите количество минут, которые вы потратили на активность"))

    elif input_time_activity > 720:
        await process_invalid_value(message, ("Вы занимались активностью больше 16 часов?\nОбратитесь к специалисту для диагностики вашего физического и ментального здоровья\n\nЕсли вы ошиблись при вводе, то введите количество минут, которые вы потратили на активность"))

    else:
        await state.update_data(time_activity=input_time_activity)
        await save_activity_log(message, state)
        await message.answer("Введите /help для вызова всех команд")



@router2.message(LogActivityStates.time_activity)
async def process_invalid_input_time_activity(message: Message):
    await message.reply("Пожалуйста, введите длительность вашей активности в минутах в диапазоне [1, 720]")



async def save_activity_log(message: Message, state: FSMContext):
    data = await state.get_data()
    activity_name = data.get("activity_name")
    calories_per_hour = data.get("ccal_in_hour_for_activity")
    minutes = data.get("time_activity")

    burned_calories = round((calories_per_hour / 60) * minutes, 2)

    timezone = pytz.timezone("Europe/Moscow")
    current_datetime = datetime.now(timezone)
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    user_id = str(message.from_user.id)

    await log_activity(user_id, activity_name, burned_calories, minutes)


    amount_water_increased = minutes / 30 * 200

    await message.reply(
        f"Вы занимались {activity_name} {minutes} минут и сожгли {burned_calories} калорий\n"
        f"в {current_datetime_str} по Москве. Событие записано\n"
        f"Количество необходимой воды увеличено на {amount_water_increased} мл\nПожалуйста выпейте {amount_water_increased} мл"
    )
    await state.clear()



