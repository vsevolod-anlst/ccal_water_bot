from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import aiohttp

from states import Profile

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("БУУ! Я бот! Не бойся!\nВведи /help для списка команд")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Команды:\n"
        "/start - Начало работы\n"
        "/set_profile - Создание вашего личного профиля"
    )

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    kb = [
        [KeyboardButton(text="Муж")],
        [KeyboardButton(text="Жен")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Ху ар ю?"
    )
    await message.answer("Выберете ваш пол", reply_markup=keyboard)
    await state.set_state(Profile.sex)

@router.message(Profile.sex)
async def process_sex_selection(message: Message, state: FSMContext):
    selected_sex = message.text
    if selected_sex not in ["Муж", "Жен"]:
        kb = [
            [KeyboardButton(text="Муж")],
            [KeyboardButton(text="Жен")]
        ]
        keyboard = ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Ху ар ю?"
        )

        await message.reply("Пожалуйста, выберите один из предложенных вариантов.", reply_markup=keyboard)
        return

    await state.update_data(sex=selected_sex)
    await message.answer("Введите как вас величать", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Profile.name)

@router.message(Profile.name)
async def process_name(message: Message, state: FSMContext):
    selected_name = message.text
    await state.update_data(name=selected_name)
    await message.answer("Введите ваш возраст")
    await state.set_state(Profile.age)

@router.message(Profile.age)
# сюда дописать доп хендлер который будет возвращать челика сюда если возраст не ОК
# https://mastergroosha.github.io/aiogram-3-guide/fsm/
async def process_age(message: Message, state: FSMContext):
    selected_age = message.text
    try:
        selected_age = int(selected_age)

        if selected_age < 0:
            await message.reply("Возраст не может быть отрицательным")
        elif selected_age == 0:
            await message.reply("Вы в 0 лет используете Телеграмм? Тогда мы идем к вам! Учиться гениальности")
        elif 0 < selected_age < 18:
            await message.reply(
                "Расчет будет верен только для сформировавшихся людей.\nКушай кашку, пей водичку и не парься.\nПодсчет калорий это для старых.")
        elif selected_age > 100:
            await message.reply(
                "Уже поздно считать калории\nКушай кашку, пей водичку и не парься.\nПодсчет калорий это для старых, но не настолько.")
        else:
            await state.update_data(age=selected_age)
    except ValueError:
        await message.reply("Введите целое положительное число")

    await message.answer("Введите ваш вес в килограммах")
    await state.set_state(Profile.weight)

@router.message(Profile.weight)
async def process_weight(message: Message, state: FSMContext):
    selected_weight = message.text
    try:
        selected_weight = float(selected_weight)

        if selected_weight < 0:
            await message.reply("Вес не может быть отрицательным")
        elif 0 <= selected_weight < 30:
            await message.reply("Вы живы вообще?\nРекомендую обратиться к специалисту")
        else:
            await state.update_data(weight=selected_weight)
    except ValueError:
        await message.reply("Введите положительное число")

    await message.answer("Введите ваш город проживания")
    await state.set_state(Profile.city)

@router.message(Profile.city)
async def process_city(message: Message, state: FSMContext):
    selected_city = message.text

    # тут нужно ходить в Вевер АПИ и если лист ответа пустой - то писать что город с таким назв не найден
    # {"message":"accurate","cod":"200","count":0,"list":[]}
    # и если таких городов больше 1 то проверять в РФ ли город: если да - то берем первый из РФ
    # если не в РФ то выводим список городов с координатами и названием старны и просим выбрать
    # надо написать в отдельный файл функцию похода и проверки 1 ли город и проверки не РФ ли страна
    # после выбора города сохраняем его в состояние

# в отдельный файл функция для сохранения инфы в файлик
# функция для проверки того нет ли пользователя в Файлике при начале работы и авторизации

@router.message()
async def handle_unrecognized_message(message: Message):
    await message.reply("Введите /help для просмотра команд")


