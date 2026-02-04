from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


back_start_button = InlineKeyboardButton(
    text="⬅️ Назад",
    callback_data="start"
)

back_start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [back_start_button]
    ]
)