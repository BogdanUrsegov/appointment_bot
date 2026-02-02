from .callback import router as callback_router
from .message import router as message_router
from aiogram import Router


fill_profile_router = Router()

fill_profile_router.include_routers(callback_router, message_router)


__all__ = [
    "fill_profile_router"
]