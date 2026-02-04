# bot/utils/slots_finder.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict
from bot.database.models import Doctor, Appointment, AppointmentStatus, Specialization


async def get_free_slots(db: AsyncSession, doctor_id: int, target_date: date) -> List[time]:
    # 1. Получаем врача
    result = await db.execute(
        select(Doctor)
        .where(Doctor.id == doctor_id, Doctor.is_active == True)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        return []
    
    # 2. Проверка рабочего дня
    day_of_week = target_date.isoweekday()
    working_days = {
        1: doctor.monday,
        2: doctor.tuesday,
        3: doctor.wednesday,
        4: doctor.thursday,
        5: doctor.friday,
        6: doctor.saturday,
        7: doctor.sunday
    }
    
    if not working_days.get(day_of_week, False):
        return []
    
    # 3. Генерация слотов
    all_slots = []
    current_time = datetime.combine(target_date, doctor.work_start_time)
    end_datetime = datetime.combine(target_date, doctor.work_end_time)
    
    while current_time + timedelta(minutes=doctor.appointment_duration_minutes) <= end_datetime:
        all_slots.append(current_time.time())
        current_time += timedelta(minutes=doctor.appointment_duration_minutes)
    
    # 4. Получаем занятые слоты
    result = await db.execute(
        select(Appointment.appointment_time)
        .where(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == target_date,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.COMPLETED])
        )
    )
    busy_slots = [row[0] for row in result.fetchall()]
    
    # 5. Свободные слоты
    return [slot for slot in all_slots if slot not in busy_slots]


async def get_free_slots_formatted(
    db: AsyncSession, 
    doctor_id: int, 
    target_date: date
) -> List[Dict[str, str]]:
    """
    Находит свободные слоты и возвращает их в удобном для отображения формате.
    
    Args:
        db: Асинхронная сессия базы данных
        doctor_id: ID врача
        target_date: Дата для поиска слотов
    
    Returns:
        List[Dict]: Список словарей с информацией о слотах
        Пример: [
            {'time': '09:00', 'display': '09:00 - 09:12'},
            {'time': '09:12', 'display': '09:12 - 09:24'},
        ]
    """
    # Получаем свободные слоты (уже async)
    free_slots = await get_free_slots(db, doctor_id, target_date)
    
    if not free_slots:
        return []

    # Получаем врача
    result = await db.execute(
        select(Doctor).where(Doctor.id == doctor_id)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        return []
    
    result_list = []
    for slot_time in free_slots:
        start_dt = datetime.combine(target_date, slot_time)
        end_dt = start_dt + timedelta(minutes=doctor.appointment_duration_minutes)
        end_time = end_dt.time()
        
        result_list.append({
            'time': slot_time.strftime('%H:%M'),
            'display': f"{slot_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}",
            'start_time': slot_time,
            'end_time': end_time
        })
    
    return result_list


def is_slot_available(db: AsyncSession, doctor_id: int, target_date: date, target_time: time) -> bool:
    """
    Проверяет, доступен ли конкретный слот для записи.
    
    Args:
        db: Сессия базы данных
        doctor_id: ID врача
        target_date: Дата приема
        target_time: Время приема
    
    Returns:
        bool: True если слот свободен, False если занят
    """
    existing = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == target_date,
        Appointment.appointment_time == target_time,
        Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.COMPLETED])
    ).first()
    
    if existing:
        return False
    
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        return False
    
    if target_time < doctor.work_start_time or target_time >= doctor.work_end_time:
        return False
    
    start_dt = datetime.combine(target_date, doctor.work_start_time)
    target_dt = datetime.combine(target_date, target_time)
    
    minutes_diff = (target_dt - start_dt).total_seconds() / 60
    if minutes_diff % doctor.appointment_duration_minutes != 0:
        return False
    
    return True


def get_available_doctors_for_date(
    db: AsyncSession, 
    target_date: date, 
    specialization_id: Optional[int] = None
) -> List[Dict]:
    """
    Находит всех активных врачей с заданной специализацией (если указана),
    у которых есть свободные слоты на указанную дату.
    
    Args:
        db: Сессия базы данных
        target_date: Дата для поиска
        specialization_id: Опциональный ID специализации
    
    Returns:
        List[Dict]: Список врачей со свободными слотами
    """
    query = db.query(Doctor).join(Specialization, Doctor.specialization_id == Specialization.id).filter(
        Doctor.is_active == True,
        Specialization.is_active == True
    )
    
    if specialization_id is not None:
        query = query.filter(Doctor.specialization_id == specialization_id)
    
    doctors = query.all()
    
    result = []
    for doctor in doctors:
        free_slots = get_free_slots(db, doctor.id, target_date)
        
        if free_slots:
            result.append({
                'id': doctor.id,
                'name': f"{doctor.last_name} {doctor.first_name} {doctor.middle_name or ''}".strip(),
                'specialization': doctor.specialization_rel.name,  # ← имя из связанной таблицы
                'cabinet': doctor.cabinet,
                'free_slots_count': len(free_slots),
                'free_slots': [slot.strftime('%H:%M') for slot in free_slots[:10]]
            })
    
    return result