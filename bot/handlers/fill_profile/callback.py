from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from bot.database.models import User
from bot.keyboards.birthdate import get_day_keyboard, get_month_keyboard, get_year_keyboard
from bot.keyboards.phone import phone_keyboard
from bot.keyboards.cancel_registration import cancel_registration_button
from bot.keyboards.start import start_menu
from bot.states.user_registration import UserRegistration
from bot.keyboards.goto_main_menu import goto_main_menu_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from sqlalchemy import update


router = Router()


# Старт регистрации
@router.callback_query(F.data == "add_data")
async def start_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(None)
    await callback.answer("Регистрация")
    await callback.message.answer(
        "👤 <b>Регистрация профиля</b>\n\n"
        "Давайте заполним вашу анкету — это займёт меньше минуты!\n\n"
        "👉 Введите <b>имя</b>:", 
        reply_markup=cancel_registration_button
    )
    await state.set_state(UserRegistration.first_name)

@router.callback_query(F.data == "cancel_registration")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🛑 <b>Регистрация отменена</b>\n\n"
        "Выберите действие",
        reply_markup=start_menu
    )
    await callback.answer()  # убирает "часики" у пользователя


# Пагинация годов
@router.callback_query(F.data.startswith("yp:"), UserRegistration.birth_year)
async def paginate_years(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "📆 Выберите <b>год</b> рождения:",
        reply_markup=get_year_keyboard(page)
    )
    await callback.answer()


# Выбор года
@router.callback_query(F.data.startswith("by:"), UserRegistration.birth_year)
async def select_year(callback: CallbackQuery, state: FSMContext):
    year = int(callback.data.split(":")[1])
    await state.update_data(birth_year=year)
    await callback.message.edit_text("📆 Выберите <b>месяц</b>:", reply_markup=get_month_keyboard())
    await state.set_state(UserRegistration.birth_month)
    await callback.answer()


# Выбор месяца
@router.callback_query(F.data.startswith("bm:"), UserRegistration.birth_month)
async def select_month(callback: CallbackQuery, state: FSMContext):
    month = int(callback.data.split(":")[1])
    data = await state.get_data()
    year = data["birth_year"]
    await state.update_data(birth_month=month)
    await callback.message.edit_text(
        f"📆 Выберите <b>день</b> ({year}-{month:02}):",
        reply_markup=get_day_keyboard(year, month)
    )
    await state.set_state(UserRegistration.birth_day)
    await callback.answer()


# Выбор дня + сохранение
@router.callback_query(F.data.startswith("bd:"), UserRegistration.birth_day)
async def select_day(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    day = int(callback.data.split(":")[1])
    data = await state.get_data()
    year = data["birth_year"]
    month = data["birth_month"]

    try:
        birth_date = date(year, month, day)
    except ValueError:
        await callback.answer("❌ Недопустимая дата", show_alert=True)
        return

    # Сохраняем в БД
    await session.execute(
        update(User),
        {
            "telegram_id": callback.from_user.id,
            "birth_date": birth_date
        }
    )
    await session.commit()

    # Переходим к телефону
    await state.update_data(birth_date=birth_date.isoformat())
    await callback.message.answer(
        "📱 Пожалуйста, отправьте ваш номер телефона:",
        reply_markup=phone_keyboard
    )
    await state.set_state(UserRegistration.phone)
    await callback.answer()