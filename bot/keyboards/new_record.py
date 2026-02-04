from datetime import date, time
from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .back_start import back_start_button
from bot.database.models import Specialization, Doctor

SPEC_CALLBACK = "spec"
DOCTOR_CALLBACK = "doc"
DATE_CALLBACK = "date"
TIME_CALLBACK = "time"


def specializations_keyboard(specializations: List[Specialization]) -> InlineKeyboardMarkup:
    """Клавиатура выбора специализации."""
    builder = InlineKeyboardBuilder()
    for spec in specializations:
        builder.button(
            text=spec.name,
            callback_data=f"{SPEC_CALLBACK}:{spec.id}"
        )
    builder.adjust(1)
    builder.row(back_start_button)
    return builder.as_markup()


def doctors_keyboard(doctors: List[Doctor]) -> InlineKeyboardMarkup:
    """Клавиатура выбора врача."""
    builder = InlineKeyboardBuilder()
    for doc in doctors:
        name_parts = [doc.last_name, doc.first_name[0] + "."]
        if doc.middle_name:
            name_parts.append(doc.middle_name[0] + ".")
        name = " ".join(name_parts)
        builder.button(
            text=name,
            callback_data=f"{DOCTOR_CALLBACK}:{doc.id}"
        )
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_specializations"))

    return builder.as_markup()


def dates_keyboard(dates: List[date]) -> InlineKeyboardMarkup:
    """Клавиатура выбора даты (следующие рабочие дни)."""
    builder = InlineKeyboardBuilder()
    for d in dates:
        # Локализованный короткий формат: "5 фев", "12 мар"
        label = (
            d.strftime("%d %b")
            .replace("Jan", "янв")
            .replace("Feb", "фев")
            .replace("Mar", "мар")
            .replace("Apr", "апр")
            .replace("May", "мая")
            .replace("Jun", "июн")
            .replace("Jul", "июл")
            .replace("Aug", "авг")
            .replace("Sep", "сен")
            .replace("Oct", "окт")
            .replace("Nov", "ноя")
            .replace("Dec", "дек")
        )
        builder.button(
            text=label,
            callback_data=f"{DATE_CALLBACK}:{d.isoformat()}"
        )
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_doctors"))
    return builder.as_markup()


def times_keyboard(times: List[time]) -> InlineKeyboardMarkup:
    """Клавиатура выбора времени (свободные слоты)."""
    builder = InlineKeyboardBuilder()
    for t in sorted(times):
        label = t.strftime("%H:%M")
        print(label)
        builder.button(
            text=label,
            callback_data=f"{TIME_CALLBACK}:{label}"
        )
    builder.adjust(3)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_dates"))
    return builder.as_markup()