from aiogram.fsm.state import StatesGroup, State


class NewRecord(StatesGroup):
    specializations = State()
    doctors = State()
    dates = State()
    slots = State()