# bot/utils/slots.py
from datetime import datetime, timedelta, date
from sqlalchemy.orm import selectinload
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models import Appointment, Doctor


def is_doctor_working_on_date(doctor: Doctor, dt: datetime) -> bool:
    """Проверяет, работает ли врач в указанный день."""
    weekday = dt.weekday()  # понедельник = 0, воскресенье = 6
    day_flags = [doctor.monday, doctor.tuesday, doctor.wednesday,
                 doctor.thursday, doctor.friday, doctor.saturday, doctor.sunday]
    if not day_flags[weekday]:
        return False

    # Проверяем, не попадает ли дата в период недоступности
    target_date = dt.date()
    for period in doctor.unavailable_periods:
        if period.start_date <= target_date <= period.end_date:
            return False
    return True

def generate_slots_for_day(doctor: Doctor, day: date) -> List[datetime]:
    """Генерирует все возможные слоты в заданный день (каждые 12 минут)."""
    if not is_doctor_working_on_date(doctor, datetime.combine(day, doctor.work_start_time)):
        return []

    start = datetime.combine(day, doctor.work_start_time)
    end = datetime.combine(day, doctor.work_end_time)

    slots = []
    current = start
    while current < end:
        slots.append(current)
        current += timedelta(minutes=12)
        # Убедимся, что последний слот не выходит за end
        if current >= end and len(slots) > 0 and slots[-1].time() >= doctor.work_end_time:
            slots.pop()
            break
    return slots

async def get_free_appointment_slots(
    session: AsyncSession,
    doctor_id: int,
    start_date: date,
    end_date: date
) -> List[datetime]:
    """Возвращает свободные слоты для врача в диапазоне дат."""
    # Загружаем врача со всеми данными
    from bot.database.models import Doctor
    result = await session.execute(
        select(Doctor)
        .where(Doctor.id == doctor_id)
        .options(
            # Подгружаем периоды недоступности
            selectinload(Doctor.unavailable_periods)
        )
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        return []

    all_possible_slots = []
    current_date = start_date
    while current_date <= end_date:
        all_possible_slots.extend(generate_slots_for_day(doctor, current_date))
        current_date += timedelta(days=1)

    if not all_possible_slots:
        return []

    # Находим занятые слоты
    result = await session.execute(
        select(Appointment.appointment_time)
        .where(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_time.in_(all_possible_slots)
        )
    )
    busy_times = {row[0] for row in result}

    return [slot for slot in all_possible_slots if slot not in busy_times]