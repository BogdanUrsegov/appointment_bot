from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

goto_main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🏠 В главное меню",
                callback_data="goto_main_menu"
            )
        ]
    ]
)