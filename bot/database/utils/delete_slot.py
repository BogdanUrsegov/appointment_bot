from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from bot.database.models import Appointment, AppointmentStatus
from datetime import date, time
from typing import Optional


async def cancel_appointment(
    session: AsyncSession,
    appointment_id: Optional[int] = None,
    *,
    patient_telegram_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    appointment_date: Optional[date] = None,
    appointment_time: Optional[time] = None
) -> bool:
    """
    Отменяет запись на приём (рекомендуется вместо физического удаления).
    
    🔹 Параметры (выберите один способ):
       • appointment_id — ID записи (предпочтительно)
       • ИЛИ комбинация: patient_telegram_id + doctor_id + appointment_date + appointment_time
    
    ✅ Возвращает: True если запись отменена, иначе False
    💡 Совет: Меняем статус на CANCELLED вместо удаления — сохраняем историю для аналитики.
    """
    # 1. Находим запись
    if appointment_id:
        stmt = select(Appointment).where(Appointment.id == appointment_id)
    elif all([patient_telegram_id, doctor_id, appointment_date, appointment_time]):
        stmt = (
            select(Appointment)
            .join(Appointment.patient)
            .where(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
                Appointment.appointment_time == appointment_time,
                Appointment.patient.has(telegram_id=patient_telegram_id)
            )
        )
    else:
        raise ValueError("Укажите appointment_id ИЛИ полную комбинацию параметров пациента/врача/времени")

    result = await session.execute(stmt)
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        return False
    
    # 2. Отменяем (не удаляем!) — сохраняем аудит
    appointment.status = AppointmentStatus.CANCELLED
    await session.commit()
    return True


async def hard_delete_appointment(
    session: AsyncSession,
    appointment_id: int
) -> bool:
    """
    🔴 Физическое удаление записи (используйте осторожно!).
    """
    stmt = delete(Appointment).where(Appointment.id == appointment_id)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0