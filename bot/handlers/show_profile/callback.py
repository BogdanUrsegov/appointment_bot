# bot/handlers/profile/handlers.py
import traceback
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.database.models import User
from bot.keyboards.profile import profile_menu
from bot.utils.user_checker import get_profile_completion_message, check_user_profile_completion


router = Router()


@router.callback_query(F.data == "my_profile")
async def handle_my_profile(callback: CallbackQuery, session: AsyncSession):
    """
    Обработчик для кнопки "Мой профиль".
    """
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("Пользователь не найден!", show_alert=True)
        return
    
    # Проверяем заполнение профиля
    check_result = check_user_profile_completion(user)

    if check_result['is_complete']:
        message_text = (
            "<b>Ваши данные:</b>\n\n"
            f"{user.last_name} {user.first_name} {user.patronymic}"
            f"Номер телефона: {user.phone}"
            )
    else:
        message_text = "<b><i>Вы ещё не заполнили свои данные</i></b>"

    reply_markup = profile_menu(check_result)

    # Отправляем или обновляем сообщение
    if callback.message:
        await callback.message.edit_text(
            message_text,
            reply_markup=reply_markup
        )
    else:
        await callback.message.answer(
            message_text,
            reply_markup=reply_markup
        )
    
    await callback.answer()
    