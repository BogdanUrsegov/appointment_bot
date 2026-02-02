# keyboards/phone.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

share_contact_button = KeyboardButton(text="📞 Отправить номер", request_contact=True)
cancel_button = KeyboardButton(text="❌ Отмена")

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[[share_contact_button], [cancel_button]],
    resize_keyboard=True,
    one_time_keyboard=True
)