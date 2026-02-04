from aiogram import Router
from .start import start_router
from .show_profile import router as profile_router
from .fill_profile import fill_profile_router
from .new_record import new_record_router
from .my_records import my_records_router

router = Router()

router.include_routers(start_router, profile_router, fill_profile_router, new_record_router, my_records_router)


__all__ = [
    "router"
]