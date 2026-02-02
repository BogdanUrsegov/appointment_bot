from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.birthdate import get_year_keyboard
from bot.keyboards.cancel_registration import cancel_registration_button
from bot.states.user_registration import UserRegistration
from sqlalchemy import update
from bot.keyboards.phone import phone_keyboard
from aiogram.types import ReplyKeyboardRemove

from bot.database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from bot.utils.validate import validate_name, validate_phone
import re


router = Router()


@router.message(UserRegistration.first_name)
async def process_first_name(message: Message, state: FSMContext):
    if validate_name(message.text):
        await state.update_data(first_name=message.text.strip())
        await message.answer("✏️ Отлично! Теперь введите <b>фамилию</b>:", reply_markup=cancel_registration_button)
        await state.set_state(UserRegistration.last_name)
    else:
        await message.answer("❌ Имя должно содержать только буквы (2–50 символов). Попробуйте снова.", reply_markup=cancel_registration_button)


@router.message(UserRegistration.last_name)
async def process_last_name(message: Message, state: FSMContext):
    if validate_name(message.text):
        await state.update_data(last_name=message.text.strip())
        await message.answer(
            "🖋️ Укажите <b>отчество</b>:\n"
            "Если его нет — напишите «<code>нет</code>».",
            reply_markup=cancel_registration_button
        )
        await state.set_state(UserRegistration.patronymic)
    else:
        await message.answer("❌ Фамилия должна содержать только буквы. Попробуйте снова.", reply_markup=cancel_registration_button)


@router.message(UserRegistration.patronymic)
async def process_patronymic(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() == "нет":
        patronymic = ""
    elif validate_name(text):
        patronymic = text
    else:
        await message.answer("❌ Некорректное отчество. Используйте только буквы.", reply_markup=cancel_registration_button)
        return

    await state.update_data(patronymic=patronymic)
    await message.answer("📆 Выберите <b>год</b> рождения:", reply_markup=get_year_keyboard())
    await state.set_state(UserRegistration.birth_year)

@router.message(UserRegistration.phone)
async def process_phone(message: Message, state: FSMContext, session: AsyncSession):
    telegram_id = message.from_user.id
    phone = None

    if message.contact:
        # Пользователь нажал «Поделиться контактом»
        phone = message.contact.phone_number
    elif message.text and validate_phone(message.text):
        # Ввёл вручную
        clean = re.sub(r"[^\d+]", "", message.text)
        phone = "+7" + clean.lstrip("87") if not clean.startswith("+") else clean
    else:
        await message.answer(
            "❌ Неверный формат.\n\n"
            "Нажмите «📞 Отправить номер» или введите вручную:\n"
            "<code>+79991234567</code>",
            reply_markup=phone_keyboard
        )
        return

    await session.execute(
        update(User),
        {
            "telegram_id": telegram_id,
            "phone": phone
        }
    )
    await session.commit()

    await message.answer(
        "✅ <b>Регистрация завершена!</b>\n\n"
        "Теперь вы можете записаться к врачу.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()