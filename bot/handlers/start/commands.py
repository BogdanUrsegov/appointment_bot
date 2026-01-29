from aiogram import Bot, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, bot: Bot):
    await message.answer(text="👋 Привет! Добро пожаловать в бота")