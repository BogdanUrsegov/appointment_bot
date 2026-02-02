from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.user_checker import get_profile_edit_keyboard


def profile_menu(check_result):
    if check_result['is_complete']:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📝 Заполнить заново", callback_data="add_data_again")]
            ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📝 Заполнить данные", callback_data="add_data")]
            ]
        )
    return keyboard