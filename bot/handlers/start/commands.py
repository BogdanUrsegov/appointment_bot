from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models import User


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, session: AsyncSession):
    telegram_id = message.from_user.id

    # Проверяем, существует ли пользователь
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is None:
        # Создаём нового пользователя
        new_user = User(telegram_id=telegram_id)
        session.add(new_user)
        await session.commit()
        await message.answer("👋 Добро пожаловать! Вы успешно зарегистрированы.")
    else:
        await message.answer("✅ С возвращением!")