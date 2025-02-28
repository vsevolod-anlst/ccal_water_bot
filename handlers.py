from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import re
import aiofiles


from states import Profile
from get_weather import get_temp


router = Router()


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


available_target = ["Похудеть", "Подсушиться без потери массы", "Набрать вес"]
kb_target = [
    [KeyboardButton(text="Похудеть")],
    [KeyboardButton(text="Подсушиться без потери массы")],
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


def check_string(text):
    return bool(re.match(r'^[A-Za-zА-Яа-яЁё-]+$', text))


async def save_user_data(user_id, data):
    async with aiofiles.open('user_data.txt', mode='a') as file:
        await file.write(f"{user_id}:{data}\n")


async def load_user_data(user_id):
    async with aiofiles.open('user_data.txt', mode='r') as file:
        async for line in file:
            uid, data = line.strip().split(':', 1)
            if uid == str(user_id):
                return eval(data)
    return

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Команды:\n"
        "/set_profile - Начало работы и создание вашего личного профиля или поиск существующего\n"
        "/delete_data - Удалить ваш профиль"
    )

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await load_user_data(user_id)
    if data:
        await message.answer(f"Заходи не бойся, уходи не плачь, {data['name']}! Ваши сохраненные данные: {data}")
        await state.update_data(**data)
    else:
        await message.answer("Пожалуйста, введите ваше имя:")
        await state.set_state(Profile.name)


@router.message(Profile.name)
async def process_name(message: Message, state: FSMContext):
    selected_name = message.text
    await state.update_data(name=selected_name)
    await message.answer("Выберете ваш пол", reply_markup=keyboard_sex)
    await state.set_state(Profile.sex)


@router.message(Profile.sex, F.text.in_(available_sex))
async def process_sex_selection(message: Message, state: FSMContext):
    selected_sex = message.text
    await state.update_data(sex=selected_sex)
    await message.answer("Введите ваш возраст", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Profile.age)


@router.message(Profile.sex)
async def handle_invalid_sex(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, выберите пол из доступных вариантов: Муж или Жен", reply_markup=keyboard_sex)


@router.message(Profile.age, F.text.isdigit())
async def process_age(message: Message, state: FSMContext):
    selected_age = int(message.text)

    if selected_age < 0:
        await message.reply("Возраст не может быть отрицательным")
        await message.answer("Введите ваш возраст в диапазоне [18, 100]")
    elif selected_age == 0:
        await message.reply("Вы в 0 лет используете Телеграмм? Тогда мы идем к вам! Учиться гениальности")
        await message.answer("Введите ваш возраст в диапазоне [18, 100]")
    elif 0 < selected_age < 18:
        await message.reply(
            "Расчет будет верен только для сформировавшихся людей.\nКушай кашку, пей водичку и не парься.\nПодсчет калорий это для старых.")
        await message.answer("Введите ваш возраст в диапазоне [18, 100]")
    elif selected_age > 100:
        await message.reply(
            "Уже поздно считать калории\nКушай кашку, пей водичку и не парься.\nПодсчет калорий это для старых, но не настолько.")
        await message.answer("Введите ваш возраст в диапазоне [18, 100]")
    else:
        await state.update_data(age=selected_age)
        await message.answer("Введите ваш вес в килограммах")
        await state.set_state(Profile.weight)


@router.message(Profile.age)
async def process_invalid_age(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, введите корректный возраст в виде числа в диапазоне [18, 100]")


@router.message(Profile.weight, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_weight(message: Message, state: FSMContext):
    selected_weight = float(message.text)

    if selected_weight < 0:
        await message.reply("Вес не может быть отрицательным")
        await message.answer("Введите ваш вес в диапазоне [30, 200]")
    elif 0 <= selected_weight < 30:
        await message.reply("Вы живы вообще?\nРекомендую обратиться к специалисту")
        await message.answer("Введите ваш вес в диапазоне [30, 200]")
    elif selected_weight > 200:
        await message.reply("Хорошего человека конечно должно быть много, но...\nОбратитесь к специалисту")
        await message.answer("Введите ваш вес в диапазоне [30, 200]")
    else:
        await state.update_data(weight=selected_weight)
        await message.answer("Введите ваш город проживания")
        await state.set_state(Profile.city)


@router.message(Profile.weight)
async def process_invalid_weight(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, введите корректный вес в виде числа в диапазоне [30, 200]")


@router.message(Profile.city)
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


def strike(text="Сказочник"):
    result = ''
    for char in text:
        result += char + '\u0336'
    return result


@router.message(Profile.cnt_active_min_for_day, F.text.regexp(r'^\d+(\.\d+)?$'))
async def process_cnt_active_min_for_day(message: Message, state: FSMContext):
    selected_cnt_active_min_for_day = float(message.text)
    if selected_cnt_active_min_for_day < 0:
        await message.reply("Количество минут активности не может быть отрицательным")
    elif selected_cnt_active_min_for_day > 3000:
        name_vrun = strike()
        await message.reply(f"В сутках 3600 минут, из них при такой нагрузке надо спать хотя бы 600 минут, {name_vrun}")
    else:
        await state.update_data(cnt_active_min_for_day=selected_cnt_active_min_for_day)
        await message.answer("Изначально установленная цель - похудетьХотите ли вы изменить эту цель?", reply_markup=keyboard_yes_no)
        await state.set_state(Profile.confirm_target)


@router.message(Profile.cnt_active_min_for_day)
async def process_invalid_cnt_active_min_for_day(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, введите положительное число для количества минут вашей активности в день в виде числа в диапазоне [0, 3000]")


@router.message(Profile.confirm_target, F.text == "Да")
async def change_target(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, выберите вашу цель:", reply_markup=keyboard_target)
    await state.set_state(Profile.target)


async def save_user_and_notify(message: Message, state: FSMContext):
    data = await state.get_data()
    user_data = {
        "sex": data.get("sex"),
        "name": data.get("name"),
        "age": data.get("age"),
        "weight": data.get("weight"),
        "city": data.get("city"),
        "cnt_active_min_for_day": data.get("cnt_active_min_for_day"),
        "target": data.get("target")
    }
    user_id = message.from_user.id
    await save_user_data(user_id, str(user_data))
    await message.answer("Ваши данные сохранены!")
    await state.clear()


@router.message(Profile.confirm_target, F.text == "Нет")
async def keep_target(message: Message, state: FSMContext):
    await state.update_data(target="Похудеть")
    await message.answer("Цель сохранена: Похудеть", reply_markup=ReplyKeyboardRemove())
    await save_user_and_notify(message, state)


@router.message(Profile.target,
                F.text.in_(available_target)
                )
async def process_target(message: Message, state: FSMContext):
    selected_target = message.text
    await state.update_data(target=selected_target)
    await message.answer(f"Цель сохранена: {selected_target}", reply_markup=ReplyKeyboardRemove())
    await save_user_and_notify(message, state)


@router.message(Profile.target)
async def invalid_target(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, выберите цель из предложенных вариантов:", reply_markup=keyboard_target)


async def delete_user_data(user_id):
    async with aiofiles.open('user_data.txt', mode='r') as file:
        lines = await file.readlines()

    async with aiofiles.open('user_data.txt', mode='w') as file:
        for line in lines:
            if not line.startswith(f"{user_id}:"):
                await file.write(line)

    return "Ваши данные удалены!"

@router.message(Command("delete_data"))
async def cmd_delete_data(message: Message, state: FSMContext):
    user_id = message.from_user.id
    result = await delete_user_data(user_id)
    await message.answer(result)


@router.message()
async def handle_unrecognized_message(message: Message):
    await message.reply("Введите /help для просмотра команд")


