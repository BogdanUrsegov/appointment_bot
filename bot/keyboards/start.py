from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
                [
                InlineKeyboardButton(
                    text="📝 Записаться к врачу",
                    callback_data="new_appointment"
                    ),
                InlineKeyboardButton(
                    text="🗓 Мои записи",
                    callback_data="my_slots"
                    )
                ]
            ]
        )
    return keyboard