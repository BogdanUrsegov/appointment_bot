from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


start_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📝 Записаться к врачу", callback_data="new_appointment")],
        [InlineKeyboardButton(text="🗓 Мои записи", callback_data="my_slots")],
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")]
    ]
)