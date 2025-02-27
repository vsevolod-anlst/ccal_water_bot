from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import re
import aiofiles


from states import Profile


router = Router()

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


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("БУУ! Я бот! Не бойся!\nВведи /help для списка команд")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Команды:\n"
        "/start - Начало работы\n"
        "/set_profile - Создание вашего личного профиля или поиск существующего"
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


@router.message(Profile.name)
async def process_name(message: Message, state: FSMContext):
    selected_name = message.text
    await state.update_data(name=selected_name)

    await message.answer("Выберете ваш пол", reply_markup=keyboard_sex)
    await state.set_state(Profile.sex)


@router.message(Profile.sex,
                F.text.in_(available_sex)
                )
async def process_sex_selection(message: Message, state: FSMContext):
    selected_sex = message.text
    await state.update_data(sex=selected_sex)
    await message.answer("Введите ваш возраст", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Profile.age)


@router.message(Profile.sex)
async def handle_invalid_sex(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, выберите пол из доступных вариантов: Муж или Жен")

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
    if check_string(selected_city):
        await state.update_data(city=selected_city)
        await message.answer(f"Вы выбрали город: {selected_city}")
        # Здесь можно добавить переход к следующему состоянию
    else:
        await message.answer("Введите название города без спец символов и цифр")

    await message.answer("Введите примерное количество минут вашей активности в день")
    await state.set_state(Profile.cnt_active_min_for_day)


@router.message(Profile.cnt_active_min_for_day)
async def process_cnt_active_min_for_day(message: Message, state: FSMContext):
    selected_cnt_active_min_for_day = message.text
    try:
        selected_cnt_active_min_for_day = float(selected_cnt_active_min_for_day)

        if selected_cnt_active_min_for_day < 0:
            await message.reply("Количество минут активности не может быть отрицательным")
        else:
            await state.update_data(cnt_active_min_for_day=selected_cnt_active_min_for_day)
    except ValueError:
        await message.reply("Введите положительное число")

    kb_target = [
        [KeyboardButton(text="Похудеть")],
        [KeyboardButton(text="Подсушиться без потери массы")],
        [KeyboardButton(text="Набрать вес")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_target,
        resize_keyboard=True,
        input_field_placeholder="Выберите вашу цель?"
    )
    await message.answer("Изначально установленная цель - похудеть\nВыберите иную, если она отличается\nИли отправьте пустое сообщение для того чтобы оставить дефолтную", reply_markup=keyboard)


available_target = ["Похудеть", "Подсушиться без потери массы", "Набрать вес"]


@router.message(Profile.target,
                F.text.in_(available_target)
                )
async def process_target(message: Message, state: FSMContext):
    selected_target = message.text
    await state.update_data(target=selected_target)

    data = await state.get_data()
    sex = data.get("sex")
    name = data.get("name")
    age = data.get("age")
    weight = data.get("weight")
    city = data.get("city")
    cnt_active_min_for_day = data.get("cnt_active_min_for_day")
    target = data.get("target")

    user_data = {
        "sex": sex,
        "name": name,
        "age": age,
        "weight": weight,
        "city": city,
        "cnt_active_min_for_day": cnt_active_min_for_day,
        "target": target
    }
    user_id = message.from_user.id

    await save_user_data(user_id, str(user_data))
    await message.answer("Ваши данные сохранены!")





    # это надо делать не тут а при рассчете ККАЛ и ВОДЫ
    #temp_in_city_now = get_temp(selected_city)


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


