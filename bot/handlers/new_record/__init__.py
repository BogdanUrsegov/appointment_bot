from .callback import router as callback_router
from aiogram import Router


new_record_router = Router()

new_record_router.include_routers(callback_router)

__all__ = [
    "new_record_router"
]
