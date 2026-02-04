from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .back_start import back_start_button
from bot.database.utils.user_checker import get_profile_edit_keyboard


def edit_data_keyboard(check_result):
    if check_result['is_complete']:
        text_button = "📝 Заполнить заново"
    else:
        text_button = "📝 Заполнить данные"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text_button, callback_data="add_data")],
            [back_start_button]

        ]
    )
    return keyboard