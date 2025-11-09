from aiogram import types, Router
from aiogram.filters import CommandStart


user_router = Router()



@user_router.message(CommandStart())
async def strt(message: types.Message):
    await message.answer(message.text)