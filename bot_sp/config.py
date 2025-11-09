import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from dotenv import find_dotenv, load_dotenv
from users import user_router
load_dotenv(find_dotenv())

ALLOWED_UPDETE = ()
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()

dp.include_router(user_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())