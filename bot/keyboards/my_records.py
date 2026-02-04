from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.database.utils.status2emoji import status2emoji
from .back_start import back_start_button


SLOT_CALLBACK = "slot"
CANCEL_SLOT_CALLBACK = "cancel_slot"


def slots_keyboard(appointments) -> InlineKeyboardMarkup:
    """Клавиатура выбора даты (следующие рабочие дни)."""
    builder = InlineKeyboardBuilder()
    for appt in appointments:
        builder.button(
            text=f"🗓 {appt['date'].strftime('%d.%m.%Y')} {appt['time'].strftime('%H:%M')} 👨‍⚕️ {appt['specialization']} {status2emoji(str(appt['status']))}",
            callback_data=f"{SLOT_CALLBACK}:{appt['id']}"
        )
    builder.adjust(1)
    builder.row(back_start_button)
    return builder.as_markup()


def cancel_slot_keyboard(slot_id) -> InlineKeyboardMarkup:
    """Клавиатура выбора даты (следующие рабочие дни)."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌ Отменить запись",
        callback_data=f"{CANCEL_SLOT_CALLBACK}:{slot_id}"
    )
    builder.button(
        text="⬅️ Назад",
        callback_data="my_slots"
    )
    builder.adjust(1)
    return builder.as_markup()