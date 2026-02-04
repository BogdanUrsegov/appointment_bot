from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models import User
from bot.keyboards.start import start_menu
from .utils import handle_start


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, session: AsyncSession):
    await handle_start(message, session)