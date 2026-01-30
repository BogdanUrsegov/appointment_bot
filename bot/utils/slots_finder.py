# bot/utils/slots_finder.py
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import extract
from bot.database.models import Doctor, Appointment, AppointmentStatus


def get_free_slots(db: Session, doctor_id: int, target_date: date) -> List[time]:
    """
    Находит все свободные 12-минутные слоты у врача на указанную дату.
    
    Args:
        db: Сессия базы данных
        doctor_id: ID врача
        target_date: Дата для поиска слотов
    
    Returns:
        List[time]: Список свободных временных слотов
    """
    
    # 1. Получаем данные врача
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active == True
    ).first()
    
    if not doctor:
        return []
    
    # 2. Проверяем, работает ли врач в этот день недели
    day_of_week = target_date.isoweekday()  # 1=понедельник, 7=воскресенье
    
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
    
    # 3. Генерируем все возможные слоты за рабочий день
    all_slots = []
    current_time = datetime.combine(target_date, doctor.work_start_time)
    end_datetime = datetime.combine(target_date, doctor.work_end_time)
    
    while current_time + timedelta(minutes=doctor.appointment_duration_minutes) <= end_datetime:
        all_slots.append(current_time.time())
        current_time += timedelta(minutes=doctor.appointment_duration_minutes)
    
    # 4. Получаем занятые слоты
    busy_slots_query = db.query(Appointment.appointment_time).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == target_date,
        Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.COMPLETED])
    )
    
    busy_slots = [slot[0] for slot in busy_slots_query.all()]
    
    # 5. Фильтруем свободные слоты
    free_slots = [slot for slot in all_slots if slot not in busy_slots]
    
    return free_slots


def get_free_slots_formatted(db: Session, doctor_id: int, target_date: date) -> List[Dict[str, str]]:
    """
    Находит свободные слоты и возвращает их в удобном для отображения формате.
    
    Args:
        db: Сессия базы данных
        doctor_id: ID врача
        target_date: Дата для поиска слотов
    
    Returns:
        List[Dict]: Список словарей с информацией о слотах
        Пример: [
            {'time': '09:00', 'display': '09:00 - 09:12'},
            {'time': '09:12', 'display': '09:12 - 09:24'},
        ]
    """
    free_slots = get_free_slots(db, doctor_id, target_date)
    
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        return []
    
    result = []
    for slot_time in free_slots:
        # Вычисляем время окончания приема
        start_dt = datetime.combine(target_date, slot_time)
        end_dt = start_dt + timedelta(minutes=doctor.appointment_duration_minutes)
        end_time = end_dt.time()
        
        result.append({
            'time': slot_time.strftime('%H:%M'),
            'display': f"{slot_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}",
            'start_time': slot_time,
            'end_time': end_time
        })
    
    return result


def is_slot_available(db: Session, doctor_id: int, target_date: date, target_time: time) -> bool:
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
    # Проверяем, есть ли уже запись на это время
    existing = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == target_date,
        Appointment.appointment_time == target_time,
        Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.COMPLETED])
    ).first()
    
    if existing:
        return False
    
    # Проверяем, что время входит в рабочие часы врача
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        return False
    
    # Проверяем рабочее время
    if target_time < doctor.work_start_time or target_time >= doctor.work_end_time:
        return False
    
    # Проверяем, что время кратно длительности приема
    start_dt = datetime.combine(target_date, doctor.work_start_time)
    target_dt = datetime.combine(target_date, target_time)
    
    minutes_diff = (target_dt - start_dt).total_seconds() / 60
    if minutes_diff % doctor.appointment_duration_minutes != 0:
        return False
    
    return True


def get_available_doctors_for_date(db: Session, target_date: date, specialization: Optional[str] = None) -> List[Dict]:
    """
    Находит всех врачей, у которых есть свободные слоты на указанную дату.
    
    Args:
        db: Сессия базы данных
        target_date: Дата для поиска
        specialization: Опциональная специализация врача
    
    Returns:
        List[Dict]: Список врачей со свободными слотами
    """
    query = db.query(Doctor).filter(Doctor.is_active == True)
    
    if specialization:
        query = query.filter(Doctor.specialization == specialization)
    
    doctors = query.all()
    
    result = []
    for doctor in doctors:
        free_slots = get_free_slots(db, doctor.id, target_date)
        
        if free_slots:
            result.append({
                'id': doctor.id,
                'name': f"{doctor.last_name} {doctor.first_name} {doctor.middle_name or ''}".strip(),
                'specialization': doctor.specialization,
                'cabinet': doctor.cabinet,
                'free_slots_count': len(free_slots),
                'free_slots': [slot.strftime('%H:%M') for slot in free_slots[:10]]  # Первые 10 слотов
            })
    
    return result