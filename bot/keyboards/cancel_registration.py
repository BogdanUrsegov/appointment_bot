from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel_registration_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_registration")]
    ]
)