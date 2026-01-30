# bot/database/models.py
from datetime import time, date
from sqlalchemy import Integer, String, Boolean, Time, Date, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, date, time
from typing import List, Optional

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_name: Mapped[str] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(50))
    middle_name: Mapped[Optional[str]] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20))
    specialization: Mapped[str] = mapped_column(String(100))

    # Рабочее время
    work_start_time: Mapped[time] = mapped_column(Time, default=time(9, 0))   # 09:00
    work_end_time: Mapped[time] = mapped_column(Time, default=time(17, 0))    # 17:00

    # Дни недели (True = работает)
    monday: Mapped[bool] = mapped_column(Boolean, default=True)
    tuesday: Mapped[bool] = mapped_column(Boolean, default=True)
    wednesday: Mapped[bool] = mapped_column(Boolean, default=True)
    thursday: Mapped[bool] = mapped_column(Boolean, default=True)
    friday: Mapped[bool] = mapped_column(Boolean, default=True)
    saturday: Mapped[bool] = mapped_column(Boolean, default=False)
    sunday: Mapped[bool] = mapped_column(Boolean, default=False)

    # Связи
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="doctor")
    unavailable_periods: Mapped[List["DoctorUnavailablePeriod"]] = relationship(
        back_populates="doctor", cascade="all, delete-orphan"
    )

class DoctorUnavailablePeriod(Base):
    """
    Периоды, когда врач НЕ принимает: отпуск, больничный, командировка.
    """
    __tablename__ = "doctor_unavailable_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)  # включительно

    doctor: Mapped["Doctor"] = relationship(back_populates="unavailable_periods")

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    appointment_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship(back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship(back_populates="appointments")