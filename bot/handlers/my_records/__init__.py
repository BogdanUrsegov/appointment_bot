from .callback import router as callback_router
from aiogram import Router


my_records_router = Router()


my_records_router.include_routers(callback_router)


__all__ = [
    "my_records_router"
]