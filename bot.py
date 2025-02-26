from aiogram import Bot, Dispatcher, types
import asyncio

from config import token
from handlers import router


bot = Bot(token=token)
dp = Dispatcher()
dp.include_router(router)

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())