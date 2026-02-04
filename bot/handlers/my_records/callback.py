from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import Appointment, Doctor, User
from bot.database.utils.my_slots import get_appointments_summary_by_telegram_id
from bot.database.utils.user_checker import check_user_profile_completion
from bot.database.utils.status2emoji import status2emoji
from bot.keyboards.edit_data import edit_data_keyboard
from bot.database.utils.delete_slot import cancel_appointment
from bot.keyboards.my_records import cancel_slot_keyboard, slots_keyboard, SLOT_CALLBACK, CANCEL_SLOT_CALLBACK
from bot.keyboards.back_start import back_start_keyboard


router = Router(name="my_slots")


@router.callback_query(F.data == "my_slots")
async def cmd_my_slots(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Просмотр моих записей 🗓"""

    await callback.answer("🗓 Мои записи")
    result = await session.execute(
        select(User).where(User.telegram_id == callback.from_user.id)
    )
    user = result.scalar_one_or_none()

    check_result = check_user_profile_completion(user)

    if check_result['is_complete']:
        user_id = callback.from_user.id
        appointments = await get_appointments_summary_by_telegram_id(session, user_id)

        if not appointments:
            await callback.message.edit_text(
                "<b>У вас нет записей к врачу.</b>",
                reply_markup=back_start_keyboard
            )
            return

        text_message = "<b>Ваши записи к врачу:</b>\n"
        reply_markup = slots_keyboard(appointments)

        await callback.message.edit_text(text_message, reply_markup=reply_markup)
    else:
        await callback.message.edit_text(
            "<b><i>Вы ещё не заполнили свои данные</i></b>",
            reply_markup=edit_data_keyboard(check_result)
        )

@router.callback_query(F.data.startswith(f"{SLOT_CALLBACK}:"))
async def slot_details(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Просмотр деталей записи по её ID."""
    await callback.answer()

    slot_id = int(callback.data.removeprefix(f"{SLOT_CALLBACK}:"))

    result = await session.execute(
        select(Appointment)
        .options(
            selectinload(Appointment.doctor).selectinload(Doctor.specialization_rel),
            selectinload(Appointment.patient)
        )
        .where(Appointment.id == slot_id)
    )
    appointment = result.scalar_one_or_none()

    if appointment is None:
        await callback.message.answer("Запись не найдена.")
        return

    doctor = appointment.doctor
    specialization = doctor.specialization_rel
    patient = appointment.patient

    appointment_datetime = appointment.appointment_datetime.strftime("%d.%m.%Y в %H:%M")

    details_message = (
        f"<b>Детали вашей записи:</b>\n\n"
        f"👤 Пациент: {patient.first_name} {patient.last_name}\n"
        f"👨‍⚕️ Врач: {doctor.last_name} {doctor.first_name} {doctor.middle_name or ''}\n"
        f"🩺 Специализация: {specialization.name}\n"
        f"📅 Дата и время: {appointment_datetime}\n"
        f"📋 Статус {status2emoji(appointment.status.value)}"
    )

    await callback.message.edit_text(details_message, reply_markup=cancel_slot_keyboard(slot_id))


@router.callback_query(F.data.startswith(f"{CANCEL_SLOT_CALLBACK}:"))
async def cancel_slot_details(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Отмена записи по её ID."""
    await callback.answer()

    slot_id = int(callback.data.removeprefix(f"{CANCEL_SLOT_CALLBACK}:"))

    success = await cancel_appointment(session, slot_id)
    
    if success:
        await callback.message.edit_text(
            "<b>✅ Ваша запись была успешно отменена.</b>",
            reply_markup=back_start_keyboard
        )
    else:
        await callback.message.edit_text(
                "<b>Не удалось отменить запись</b>\n\n"
                "<i>Пожалуйста, попробуйте позже</i>",
                reply_markup=back_start_keyboard
            )