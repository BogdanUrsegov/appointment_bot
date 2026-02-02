from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models import User
from bot.keyboards.start import start_menu


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
    await message.answer(
        "👋 <b>Здравствуйте!</b>\n\n"
        "<i>Запишитесь к врачу в удобное для вас время!</i>",
        reply_markup=start_menu
        )