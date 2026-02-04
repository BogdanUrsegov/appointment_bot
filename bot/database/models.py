from datetime import time, date
from sqlalchemy import Integer, String, Boolean, Time, Date, ForeignKey, DateTime, BigInteger, Enum, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime, date, time
from typing import List, Optional
import enum

class Base(DeclarativeBase):
    pass

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    patronymic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # ← заменено
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    appointments: Mapped[List["Appointment"]] = relationship(
        back_populates="patient", 
        cascade="all, delete-orphan"
    )
    

class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))
    cabinet: Mapped[str] = mapped_column(String(50), nullable=False)
    
    work_start_time: Mapped[time] = mapped_column(Time, default=time(9, 0))
    work_end_time: Mapped[time] = mapped_column(Time, default=time(18, 0))
    appointment_duration_minutes: Mapped[int] = mapped_column(Integer, default=12)

    # Дни недели: True — работает, False — выходной
    mon: Mapped[bool] = mapped_column(Boolean, default=True)
    tue: Mapped[bool] = mapped_column(Boolean, default=True)
    wed: Mapped[bool] = mapped_column(Boolean, default=True)
    thu: Mapped[bool] = mapped_column(Boolean, default=True)
    fri: Mapped[bool] = mapped_column(Boolean, default=True)
    sat: Mapped[bool] = mapped_column(Boolean, default=False)  # Суббота часто нерабочая

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    appointments: Mapped[List["Appointment"]] = relationship(back_populates="doctor", cascade="all, delete-orphan")
    
    specialization_id: Mapped[int] = mapped_column(
        ForeignKey("specializations.id"),
        nullable=False
    )
    
    specialization_rel: Mapped["Specialization"] = relationship(
        "Specialization",
        back_populates="doctors"
    )


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_time: Mapped[time] = mapped_column(Time, nullable=False)
    appointment_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(Enum(AppointmentStatus, name="appointment_status"), default=AppointmentStatus.SCHEDULED)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient: Mapped["User"] = relationship(back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship(back_populates="appointments")

    def __init__(self, **kwargs):
        if 'appointment_date' in kwargs and 'appointment_time' in kwargs:
            date_part = kwargs['appointment_date']
            time_part = kwargs['appointment_time']
            kwargs['appointment_datetime'] = datetime.combine(date_part, time_part)
        super().__init__(**kwargs)

class Specialization(Base):
    __tablename__ = "specializations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)  # можно отключать, не удаляя
    
    # Опционально: для сортировки в интерфейсе
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    doctors: Mapped[List["Doctor"]] = relationship(
        "Doctor",
        back_populates="specialization_rel"  # ← Указывает на поле specialization_rel в Doctor
    )