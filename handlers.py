from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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
        [KeyboardButton(text="Мужской")],
        [KeyboardButton(text="Женский")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)
    await message.answer("Выберете ваш пол", reply_markup=keyboard)

@router.message()
async def handle_unrecognized_message(message: Message):
    await message.reply("Введите /help для просмотра команд")


