from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models import Appointment, AppointmentStatus, Doctor, Specialization, User


async def get_appointments_by_user_id(session: AsyncSession, user_id: int):
    """
    Получает все записи (appointments) пациента по его user.id.
    
    :param session: Асинхронная сессия SQLAlchemy
    :param user_id: ID пользователя из таблицы users
    :return: Список объектов Appointment
    """
    result = await session.execute(
        select(Appointment)
        .where(Appointment.patient_id == user_id)
        .order_by(Appointment.appointment_datetime)
    )
    return list(result.scalars().all())


async def get_appointments_summary_by_telegram_id(session: AsyncSession, telegram_id: int):
    """
    Возвращает список записей пользователя по его telegram_id в виде:
    [
        {
            "id": int,
            "date": date,
            "time": time,
            "specialization": str,
            "status": str
        },
        ...
    ]
    От самых ранних к самым поздним.
    """
    # Сначала получаем user.id по telegram_id
    user_result = await session.execute(
        select(User.id).where(User.telegram_id == telegram_id)
    )
    user_id = user_result.scalar()

    if user_id is None:
        return []  # Пользователь не найден

    # Запрос записей с данными врача и специализации
    stmt = (
        select(
            Appointment.id,
            Appointment.appointment_date.label("date"),
            Appointment.appointment_time.label("time"),
            Specialization.name.label("specialization"),
            Appointment.status.label("status")
        )
        .select_from(Appointment)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .join(Specialization, Doctor.specialization_id == Specialization.id)
        .where(
            Appointment.patient_id == user_id,
            Appointment.status != AppointmentStatus.CANCELLED
        )
        .order_by(Appointment.appointment_datetime)
    )

    result = await session.execute(stmt)
    rows = result.fetchall()

    return [
        {
            "id": row.id,
            "date": row.date,
            "time": row.time,
            "specialization": row.specialization,
            "status": row.status
        }
        for row in rows
    ]