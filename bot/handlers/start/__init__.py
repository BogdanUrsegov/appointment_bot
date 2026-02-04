from aiogram import Router

from .commands import router as command_router
from .callback import router as callback_router

start_router = Router()

start_router.include_routers(command_router, callback_router)


__all__ = [
    "start_router"
]