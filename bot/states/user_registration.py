from aiogram.fsm.state import StatesGroup, State

class UserRegistration(StatesGroup):
    first_name = State()
    last_name = State()
    patronymic = State()
    birth_year = State()
    birth_month = State()
    birth_day = State()
    phone = State()