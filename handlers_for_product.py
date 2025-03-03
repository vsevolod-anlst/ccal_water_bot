from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import re
import aiofiles
from datetime import datetime
import pytz


from states import LogWaterStates, LogFoodStates
from work_with_json_file import log_water

router2 = Router()


async def process_invalid_value(message: Message, prompt: str):
    await message.reply(prompt)

@router2.message(Command("log_water"))
async def cmd_help(message: Message, state: FSMContext):
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
        await message.reply(f"Вы выпили {input_water} миллилитров воды в {current_datetime} по Москве. Событие записано")
        await state.clear()

@router2.message(LogWaterStates.water_volume)
async def process_invalid_input_water(message: Message):
    await message.reply("Пожалуйста, введите объем выпитой воды в миллилитрах в виде числа в диапазоне [1, 5000]")