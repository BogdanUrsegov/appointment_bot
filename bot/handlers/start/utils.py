from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models import User
from bot.keyboards.start import start_menu


async def handle_start(message, session: AsyncSession):
    answer_text = (
        "👋 <b>Здравствуйте!</b>\n\n"
        "<i>Запишитесь к врачу в удобное для вас время!</i>"
        )
    
    if isinstance(message, types.CallbackQuery):
        await message.answer()
        message = message.message
        await message.edit_text(
            answer_text,
            reply_markup=start_menu
        )
    else:
        await message.answer(
            answer_text,
            reply_markup=start_menu
        )
        
    telegram_id = message.from_user.id

    # Проверяем, существует ли пользователь
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is None:
        # Создаём нового пользователя
        new_user = User(telegram_id=telegram_id)
        session.add(new_user)
        await session.commit()