from aiogram import Router

from .commands import router as command_router

start_router = Router()

start_router.include_router(command_router)


__all__ = [
    "start_router"
]