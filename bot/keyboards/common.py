# keyboards/common.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Инлайн-кнопка отмены
cancel_inline_button = InlineKeyboardButton(
    text="❌ Отмена",
    callback_data="cancel_registration"
)

# Инлайн-клавиатура с отменой
cancel_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[cancel_inline_button]]
)