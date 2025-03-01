from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import re
import aiofiles


from states import Profile
from get_weather import get_temp
from work_with_json_file import save_user_data, load_user_data_ccal_and_water, delete_user_data
from calculation_calorie_and_water_allowance import calculation_calorie_without_weather, calculation_water_without_weather


router1 = Router()


available_sex = ["Муж", "Жен"]
kb_sex = [
    [KeyboardButton(text="Муж")],
    [KeyboardButton(text="Жен")]
]
keyboard_sex = ReplyKeyboardMarkup(
    keyboard=kb_sex,
    resize_keyboard=True,
    input_field_placeholder="Ху ар ю?"
)


available_target = ["Похудеть", "Сохранить вес", "Набрать вес"]
kb_target = [
    [KeyboardButton(text="Похудеть")],
    [KeyboardButton(text="Сохранить вес")],
    [KeyboardButton(text="Набрать вес")]
]
keyboard_target = ReplyKeyboardMarkup(
    keyboard=kb_target,
    resize_keyboard=True,
    input_field_placeholder="Выберите вашу цель"
)


kb_yes_no = [
    [KeyboardButton(text="Да")],
    [KeyboardButton(text="Нет")]
]
keyboard_yes_no = ReplyKeyboardMarkup(
    keyboard=kb_yes_no,
    resize_keyboard=True,
    input_field_placeholder="Хотите ли вы изменить предустановленную цель?"
)


kb_yes_no_delete = [
    [KeyboardButton(text="Да")],
    [KeyboardButton(text="Нет")]
]
keyboard_yes_no_delete = ReplyKeyboardMarkup(
    keyboard=kb_yes_no_delete,
    resize_keyboard=True,
    input_field_placeholder="Если нажмете да - будут удалены все данные о вас"
)


def check_string(text):
    return bool(re.match(r'^[A-Za-zА-Яа-яЁё-]+$', text))




@router1.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Команды:\n"
        "/profile - Начало работы и создание вашего личного профиля или поиск существующего\n"
        "/delete_profile - Удалить ваш профиль"
    )
# РАБОТА С ФАЙЛОМ
@router1.message(Command("profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)

    result = await load_user_data_ccal_and_water(user_id)

    if isinstance(result, tuple):
        sex, name, age, weight, height, city, cnt_active_min_for_day, target, calculation_calorie, calculation_water_without_weather = await load_user_data_ccal_and_water(user_id)
        user_data_str = (f"Пол: {sex}\nИмя: {name}\nВозраст: {age}\nВес: {weight}\n"
                         f"Рост: {height}\nГород: {city}\nАктивность: {cnt_active_min_for_day} минут в день\nЦель: {target}\nНеобходимое количество калорий на день: {calculation_calorie}\nНеобходимое количество воды при условии нормальной (<25°C) температуры: {calculation_water_without_weather}")
        await message.answer(f"Заходи не бойся, уходи не плачь, {name}\nВаши сохраненные данные:\n\n{user_data_str}")
    else:
        await message.answer("Пожалуйста, введите ваше имя:")
        await state.set_state(Profile.name)


@router1.message(Profile.name)
async def process_name(message: Message, state: FSMContext):
    selected_name = message.text
    await state.update_data(name=selected_name)
    await message.answer("Выберете ваш пол", reply_markup=keyboard_sex)
    await state.set_state(Profile.sex)


@router1.message(Profile.sex, F.text.in_(available_sex))
async def process_sex_selection(message: Message, state: FSMContext):
    selected_sex = message.text
    await state.update_data(sex=selected_sex)
    await message.answer("Введите ваш возраст", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Profile.age)


@router1.message(Profile.sex)
async def handle_invalid_sex(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, выберите пол из доступных вариантов: Муж или Жен", reply_markup=keyboard_sex)


async def process_invalid_value(message: Message, prompt: str):
    await message.reply(prompt)

@router1.message(Profile.age, F.text.isdigit())
async def process_age(message: Message, state: FSMContext):
    selected_age = int(message.text)

    if selected_age < 0:
        await process_invalid_value(message, ("Возраст не может быть отрицательным\n\nПожалуйста, введите корректный возраст в диапазоне [18, 100]"))
    elif selected_age == 0:
        await process_invalid_value(message, ("Вы в 0 лет используете Телеграмм? Тогда мы идем к вам! Учиться гениальности\n\nПожалуйста, введите корректный возраст в диапазоне [18, 100]"))
    elif 0 < selected_age < 18:
        await process_invalid_value(message, ("Расчет будет верен только для сформировавшихся людей.\nКушай кашку, пей водичку и не парься.\nПодсчет калорий это для старых\n\nПожалуйста, введите корректный возраст в диапазоне [18, 100]"))
    elif selected_age > 100:
        await process_invalid_value(message, ("Уже поздно считать калории\nКушай кашку, пей водичку и не парься.\nПодсчет калорий это для старых, но не настолько\n\nПожалуйста, введите корректный возраст в диапазоне [18, 100]"))
    else:
        await state.update_data(age=selected_age)
        await message.answer("Введите ваш вес в килограммах")
        await state.set_state(Profile.weight)


@router1.message(Profile.age)
async def process_invalid_age(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, введите корректный возраст в виде числа в диапазоне [18, 100]")


@router1.message(Profile.weight, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_weight(message: Message, state: FSMContext):
    selected_weight = float(message.text)

    if selected_weight < 0:
        await process_invalid_value(message, ("Вес не может быть отрицательным\n\nВведите ваш вес в килограммах в диапазоне [30, 200]"))
    elif 0 <= selected_weight < 30:
        await process_invalid_value(message, ("Вы живы вообще?\nРекомендую обратиться к специалисту\n\nВведите ваш вес в килограммах в диапазоне [30, 200]"))
    elif selected_weight > 200:
        await process_invalid_value(message, ("Хорошего человека конечно должно быть много, но...\nОбратитесь к специалисту\n\nВведите ваш вес в килограммах в диапазоне [30, 200]"))
    else:
        await state.update_data(weight=selected_weight)
        await message.answer("Введите ваш рост в сантиметрах")
        await state.set_state(Profile.height)


@router1.message(Profile.weight)
async def process_invalid_weight(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, введите корректный вес в килограммах в виде числа в диапазоне [30, 200]")


@router1.message(Profile.height, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_height(message: Message, state: FSMContext):
    selected_height = float(message.text)

    if selected_height < 0:
        await process_invalid_value(message, ("Рост не может быть отрицательным\n\nВведите ваш рост в сантиметрах в диапазоне [55, 251]"))
    elif 0 <= selected_height < 55:
        await process_invalid_value(message, ("Самый низкий взрослый(18+) человек в мире имеет рост 55 см\nКто ты, воин?\n\nВведите ваш рост в сантиметрах в диапазоне [55, 251]"))
    elif selected_height > 251:
        await process_invalid_value(message, ("Самый высокий взрослый(18+) человек в мире имеет рост 251 см\nСупермутант обнаружен, зеленый уровень угрозы!\n\nВведите ваш рост в сантиметрах в диапазоне [55, 251]"))
    else:
        await state.update_data(height=selected_height)
        await message.answer("Введите ваш город проживания")
        await state.set_state(Profile.city)


@router1.message(Profile.height)
async def process_invalid_height(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, введите корректный рост в сантиметрах в виде числа в диапазоне [55, 251]")


@router1.message(Profile.city)
async def process_city(message: Message, state: FSMContext):
    selected_city = message.text

    if check_string(selected_city):
        temp = await get_temp(selected_city)
        if isinstance(temp, (int, float)):
            await state.update_data(city=selected_city)
            await message.answer(f"Температура за бортом {temp}°C")
            await message.answer("Введите примерное количество минут вашей активности в день")
            await state.set_state(Profile.cnt_active_min_for_day)
        else:
            await handle_invalid_city(message, temp)
    else:
        await message.answer("Введите название города без спец символов и цифр")


async def handle_invalid_city(message: Message, error_msg=None):
    if error_msg:
        await message.reply(f"Ошибка: {error_msg}")
    await message.reply("Пожалуйста, введите корректное название города без спец символов и цифр.")


@router1.message(Profile.cnt_active_min_for_day, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_cnt_active_min_for_day(message: Message, state: FSMContext):
    selected_cnt_active_min_for_day = float(message.text)
    if selected_cnt_active_min_for_day < 0:
        await process_invalid_value(message, ("Количество минут активности не может быть отрицательным\n\nВведите количество минут вашей активности в день в диапазоне [0, 3000]"))
    elif selected_cnt_active_min_for_day > 3000:
        await process_invalid_value(message, ("В сутках 3600 минут, из них при такой нагрузке надо спать хотя бы 600 минут\n\nВведите количество минут вашей активности в день в диапазоне [0, 3000]"))
    else:
        await state.update_data(cnt_active_min_for_day=selected_cnt_active_min_for_day)
        await message.answer("Изначально установленная цель - похудеть\nХотите ли вы изменить эту цель?", reply_markup=keyboard_yes_no)
        await state.set_state(Profile.confirm_target)


@router1.message(Profile.cnt_active_min_for_day)
async def process_invalid_cnt_active_min_for_day(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, введите положительное число количества минут вашей активности в день в виде числа в диапазоне [0, 3000]")


@router1.message(Profile.confirm_target, F.text == "Да")
async def change_target(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, выберите вашу цель:", reply_markup=keyboard_target)
    await state.set_state(Profile.target)

# Работа с ФАЙЛОМ
async def save_user_and_notify(message: Message, state: FSMContext):
    data = await state.get_data()
    user_data = {
        "sex": data.get("sex"),
        "name": data.get("name"),
        "age": data.get("age"),
        "weight": data.get("weight"),
        "height": data.get("height"),
        "city": data.get("city"),
        "cnt_active_min_for_day": data.get("cnt_active_min_for_day"),
        "target": data.get("target")
    }
    user_id = message.from_user.id

    await save_user_data(user_id, user_data)
    await state.clear()

    calculation_calories = await calculation_calorie_without_weather(user_id)
    calculation_water = await calculation_water_without_weather(user_id)
    await delete_user_data(user_id)
    user_data["calculation_calorie"] = calculation_calories
    user_data["calculation_water_without_weather"] = calculation_water



    await save_user_data(user_id, user_data)
    await message.answer("Ваши данные сохранены!")



@router1.message(Profile.confirm_target, F.text == "Нет")
async def keep_target(message: Message, state: FSMContext):
    await state.update_data(target="Похудеть")
    await message.answer("Цель сохранена: Похудеть", reply_markup=ReplyKeyboardRemove())
    await save_user_and_notify(message, state)
    await state.clear()


@router1.message(Profile.target, F.text.in_(available_target))
async def process_target(message: Message, state: FSMContext):
    selected_target = message.text
    await state.update_data(target=selected_target)
    await message.answer(f"Цель сохранена: {selected_target}", reply_markup=ReplyKeyboardRemove())
    await save_user_and_notify(message, state)
    await state.clear()


@router1.message(Profile.target)
async def invalid_target(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, выберите цель из предложенных вариантов:", reply_markup=keyboard_target)


@router1.message(Command("delete_profile"))
async def cmd_confirm_delete_profile(message: Message, state: FSMContext):
    await message.reply("Вы уверены, что хотите удалить ваш профиль? Нажмите 'Да' или 'Нет'", reply_markup=keyboard_yes_no_delete)
    await state.set_state(Profile.confirm_delete)


@router1.message(Profile.confirm_delete)
async def process_delete_profile(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        user_id = message.from_user.id
        result = await delete_user_data(user_id)
        await message.answer(result, reply_markup=ReplyKeyboardRemove())
        await state.clear()
    elif message.text.lower() == "нет":
        await message.answer("Ваши данные не удалены", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer("Пожалуйста, нажмите 'Да' или 'Нет'", reply_markup=keyboard_yes_no_delete)


@router1.message()
async def handle_unrecognized_message(message: Message):
    await message.reply("Введите /help для просмотра команд")


