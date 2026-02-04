from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import Specialization, Doctor, Appointment, AppointmentStatus
from typing import List
from datetime import date, datetime, timedelta
from sqlalchemy import and_, func
from datetime import time


async def get_all_specializations(session: AsyncSession):
    stmt = (
        select(Specialization)
        .where(Specialization.is_active.is_(True))
        .order_by(Specialization.sort_order)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_doctors_by_specialization(session: AsyncSession, specialization_id: int):
    stmt = (
        select(Doctor)
        .where(
            Doctor.specialization_id == specialization_id,
            Doctor.is_active.is_(True)
        )
        .order_by(Doctor.last_name, Doctor.first_name)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


def _is_workday(doctor: Doctor, check_date: date) -> bool:
    weekday = check_date.weekday()  # Monday=0, Sunday=6
    day_map = {
        0: doctor.mon,
        1: doctor.tue,
        2: doctor.wed,
        3: doctor.thu,
        4: doctor.fri,
        5: doctor.sat,
        6: False  # Воскресенье — всегда выходной (по вашей модели)
    }
    return day_map.get(weekday, False)

async def get_available_dates_for_doctor(
    session: AsyncSession,
    doctor_id: int,
    from_date: date = None,
    days_ahead: int = 20
) -> List[date]:
    if from_date is None:
        from_date = date.today()

    # Загружаем врача
    stmt = select(Doctor).where(Doctor.id == doctor_id, Doctor.is_active.is_(True))
    result = await session.execute(stmt)
    doctor = result.scalar_one_or_none()
    if not doctor:
        return []

    work_dates = []
    current = from_date + timedelta(days=1)  # начиная с завтрашнего дня
    end_date = from_date + timedelta(days=days_ahead)

    while current <= end_date:
        if _is_workday(doctor, current):
            work_dates.append(current)
        current += timedelta(days=1)

    return work_dates

async def get_free_slots_for_doctor_on_date(
    session: AsyncSession,
    doctor_id: int,
    target_date: date
) -> List[time]:
    # Получаем врача
    stmt = select(Doctor).where(Doctor.id == doctor_id)
    result = await session.execute(stmt)
    doctor = result.scalar_one_or_none()
    if not doctor:
        return []

    # Проверяем, работает ли врач в этот день
    if not _is_workday(doctor, target_date):
        return []

    # Получаем уже занятые времена
    busy_stmt = (
        select(Appointment.appointment_time)
        .where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == target_date,
                Appointment.status != AppointmentStatus.CANCELLED  # отменённые — свободны
            )
        )
    )
    busy_result = await session.execute(busy_stmt)
    busy_times = {row[0] for row in busy_result.fetchall()}

    # Генерируем все возможные слоты
    start = datetime.combine(target_date, doctor.work_start_time)
    end = datetime.combine(target_date, doctor.work_end_time)
    duration = timedelta(minutes=doctor.appointment_duration_minutes)

    free_slots = []
    current = start
    while current + duration <= end:
        slot_time = current.time()
        if slot_time not in busy_times:
            free_slots.append(slot_time)
        current += duration

    return free_slots