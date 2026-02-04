from datetime import date, time, datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.utils.user_checker import check_user_profile_completion
from bot.keyboards.edit_data import edit_data_keyboard
from bot.keyboards.start import start_menu

from bot.states.new_record import NewRecord
from bot.keyboards.new_record import (
    specializations_keyboard,
    doctors_keyboard,
    dates_keyboard,
    times_keyboard,
    SPEC_CALLBACK,
    DOCTOR_CALLBACK,
    DATE_CALLBACK,
    TIME_CALLBACK
)
from bot.database.utils.new_record import (
    get_all_specializations,
    get_doctors_by_specialization,
    get_available_dates_for_doctor,
    get_free_slots_for_doctor_on_date
)
from bot.database.models import Appointment, AppointmentStatus, Doctor, User


router = Router(name="new_record")


# === СТАРТ ЗАПИСИ ===
@router.callback_query(F.data == "new_record")
async def cmd_new_record(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Начало процесса записи к врачу 📅"""
    await callback.answer()

    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()

    check_result = check_user_profile_completion(user)

    if check_result['is_complete']:
        specializations = await get_all_specializations(session)
        if not specializations:
            await callback.message.edit_text(
                "😔 <b>К сожалению, сейчас нет доступных специализаций</b>\n\n"
                "<i>Попробуйте позже или свяжитесь с администратором</i>"
            )
            return

        await state.set_state(NewRecord.specializations)
        await callback.message.edit_text(
            "<b>Выберите специализацию врача:</b>",
            reply_markup=specializations_keyboard(specializations)
        )
    else:
        await callback.message.edit_text(
            "🛑 <b>Для записи к врачу необходимо заполнить профиль</b>",
            reply_markup=edit_data_keyboard(check_result)
        )


# === ВЫБОР СПЕЦИАЛИЗАЦИИ ===
@router.callback_query(F.data.startswith(f"{SPEC_CALLBACK}:"), NewRecord.specializations)
async def select_specialization(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession
):
    await callback.answer()

    spec_id = int(callback.data.split(":")[1])
    await state.update_data(specialization_id=spec_id)

    doctors = await get_doctors_by_specialization(session, spec_id)

    if not doctors:
        specializations = await get_all_specializations(session)
        await callback.message.edit_text(
            "😔 <b>Нет доступных врачей этой специализации</b>\n\n"
            "<i>Попробуйте выбрать другую</i>",
            reply_markup=specializations_keyboard(specializations)
        )
        return

    await state.set_state(NewRecord.doctors)
    await callback.message.edit_text(
        "<b>Выберите врача:</b>",
        reply_markup=doctors_keyboard(doctors)
    )


# === ВЫБОР ВРАЧА ===
@router.callback_query(F.data.startswith(f"{DOCTOR_CALLBACK}:"), NewRecord.doctors)
async def select_doctor(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession
):
    await callback.answer()

    doctor_id = int(callback.data.split(":")[1])
    await state.update_data(doctor_id=doctor_id)

    dates = await get_available_dates_for_doctor(session, doctor_id)

    if not dates:
        data = await state.get_data()
        spec_id = data["specialization_id"]
        doctors = await get_doctors_by_specialization(session, spec_id)
        await callback.message.edit_text(
            "😔 <b>У этого врача нет доступных записей на ближайшие дни</b>\n\n"
            "<i>Выберите другого врача</i>",
            reply_markup=doctors_keyboard(doctors)
        )
        return

    await state.set_state(NewRecord.dates)
    await callback.message.edit_text(
        "<b>Выберите дату приёма:</b>",
        reply_markup=dates_keyboard(dates)
    )


# === ВЫБОР ДАТЫ ===
@router.callback_query(F.data.startswith(f"{DATE_CALLBACK}:"), NewRecord.dates)
async def select_date(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession
):
    await callback.answer()

    target_date = date.fromisoformat(callback.data.split(":")[1])
    await state.update_data(appointment_date=target_date.isoformat())  # ← строка!

    data = await state.get_data()
    doctor_id = data["doctor_id"]

    slots = await get_free_slots_for_doctor_on_date(session, doctor_id, target_date)

    if not slots:
        dates = await get_available_dates_for_doctor(session, doctor_id)
        await callback.message.edit_text(
            f"😔 <b>На {target_date.strftime('%d.%m.%Y')} нет свободных слотов</b>\n\n"
            "<i>Выберите другую дату</i>",
            reply_markup=dates_keyboard(dates)
        )
        return
    await state.set_state(NewRecord.slots)
    await callback.message.edit_text(
        f"<b>Выберите время на {target_date.strftime('%d.%m.%Y')}</b>",
        reply_markup=times_keyboard(slots)
    )


# === ВЫБОР ВРЕМЕНИ И ПОДТВЕРЖДЕНИЕ ===
@router.callback_query(F.data.startswith(f"{TIME_CALLBACK}:"), NewRecord.slots)
async def select_time(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession
):
    await callback.answer()
    # Парсим время
    time_str = callback.data.removeprefix("time:")
    appointment_time = time.fromisoformat(time_str)

    # Получаем данные из FSM
    data = await state.get_data()
    doctor_id = data["doctor_id"]
    appointment_date = date.fromisoformat(data["appointment_date"])

    # Находим или создаём пользователя по telegram_id
    telegram_id = callback.from_user.id
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(telegram_id=telegram_id)
        session.add(user)
        await session.flush()  # Получаем user.id без коммита

    # Создаём запись на приём
    new_appointment = Appointment(
        patient_id=user.id,  # ← внутренний ID из таблицы users
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status=AppointmentStatus.SCHEDULED
    )
    session.add(new_appointment)
    await session.commit()

    # Получаем данные врача через ORM (без сырого SQL!)
    stmt = select(Doctor).options(selectinload(Doctor.specialization_rel)).where(Doctor.id == doctor_id)
    result = await session.execute(stmt)
    doctor_obj = result.scalar_one_or_none()

    if doctor_obj:
        name_parts = [doctor_obj.last_name, f"{doctor_obj.first_name[0]}."]
        if doctor_obj.middle_name:
            name_parts.append(f"{doctor_obj.middle_name[0]}.")
        doctor_name = " ".join(name_parts)
        spec_name = doctor_obj.specialization_rel.name
    else:
        doctor_name = "Неизвестный врач"
        spec_name = "—"

    await callback.message.edit_text(
        "✅ <b>Запись успешно создана!</b>\n\n"
        f"👨‍⚕️ <b>Врач:</b> {doctor_name}\n"
        f"⚕️ <b>Специализация:</b> {spec_name}\n"
        f"📅 <b>Дата:</b> {appointment_date.strftime('%d.%m.%Y')}\n"
        f"⏰ <b>Время:</b> {appointment_time.strftime('%H:%M')}\n\n"
        "Не забудьте прийти вовремя! 😊",
        reply_markup=start_menu
    )

    await state.clear()


# === КНОПКИ "НАЗАД" ===
@router.callback_query(F.data == "back_to_specializations", NewRecord.doctors)
async def back_to_specializations(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    specializations = await get_all_specializations(session)
    await state.set_state(NewRecord.specializations)
    await callback.message.edit_text(
        "<b>Выберите специализацию врача:</b>",
        reply_markup=specializations_keyboard(specializations)
    )


@router.callback_query(F.data == "back_to_doctors", NewRecord.dates)
async def back_to_doctors(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    data = await state.get_data()
    spec_id = data.get("specialization_id")
    if spec_id is None:
        await state.clear()
        await cmd_new_record(callback.message, state, session)
        return
    doctors = await get_doctors_by_specialization(session, spec_id)
    await state.set_state(NewRecord.doctors)
    await callback.message.edit_text(
        "<b>Выберите врача:</b>",
        reply_markup=doctors_keyboard(doctors)
    )


@router.callback_query(F.data == "back_to_dates", NewRecord.slots)
async def back_to_dates(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    data = await state.get_data()
    doctor_id = data.get("doctor_id")
    if doctor_id is None:
        await state.clear()
        await cmd_new_record(callback.message, state, session)
        return
    dates = await get_available_dates_for_doctor(session, doctor_id)
    await state.set_state(NewRecord.dates)
    await callback.message.edit_text(
        "<b>Выберите дату приёма:</b>",
        reply_markup=dates_keyboard(dates)
    )