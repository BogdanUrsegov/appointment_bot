from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import calendar
from datetime import datetime
from bot.keyboards.cancel_registration import cancel_registration_button

CURRENT_YEAR = datetime.now().year
MIN_YEAR = 1950
MAX_YEAR = CURRENT_YEAR - 14


def get_year_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    years = list(range(MAX_YEAR, MIN_YEAR - 1, -1))
    page_size = 6

    start = page * page_size
    end = start + page_size
    page_years = years[start:end]

    buttons = []
    for i in range(0, len(page_years), 2):
        row = [
            InlineKeyboardButton(text=str(page_years[i]), callback_data=f"by:{page_years[i]}")
        ]
        if i + 1 < len(page_years):
            row.append(
                InlineKeyboardButton(text=str(page_years[i + 1]), callback_data=f"by:{page_years[i + 1]}")
            )
        buttons.append(row)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"yp:{page - 1}"))
    if end < len(years):
        nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"yp:{page + 1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append(cancel_registration_button.inline_keyboard[0])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_month_keyboard() -> InlineKeyboardMarkup:
    months = [
        "Янв", "Фев", "Мар", "Апр", "Май", "Июн",
        "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"
    ]
    buttons = []
    for i in range(0, 12, 3):
        row = [
            InlineKeyboardButton(text=months[i], callback_data=f"bm:{i + 1}")
        ]
        if i + 1 < 12:
            row.append(InlineKeyboardButton(text=months[i + 1], callback_data=f"bm:{i + 2}"))
        if i + 2 < 12:
            row.append(InlineKeyboardButton(text=months[i + 2], callback_data=f"bm:{i + 3}"))
        buttons.append(row)

    buttons.append(cancel_registration_button.inline_keyboard[0])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_day_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    days_in_month = calendar.monthrange(year, month)[1]
    buttons = []
    row = []
    for day in range(1, days_in_month + 1):
        row.append(InlineKeyboardButton(text=str(day), callback_data=f"bd:{day}"))
        if len(row) == 7:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append(cancel_registration_button.inline_keyboard[0])

    return InlineKeyboardMarkup(inline_keyboard=buttons)