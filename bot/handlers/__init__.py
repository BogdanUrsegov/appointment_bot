from aiogram import Router
from .start import start_router
from .show_profile import router as profile_router
from .fill_profile import fill_profile_router

router = Router()

router.include_routers(start_router, profile_router, fill_profile_router)


__all__ = [
    "router"
]