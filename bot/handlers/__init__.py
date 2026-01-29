from aiogram import Router
from .start import start_router


router = Router()

router.include_router(start_router)


__all__ = [
    "router"
]