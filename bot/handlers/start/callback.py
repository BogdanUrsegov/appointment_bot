from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from .utils import handle_start


router = Router()


@router.callback_query(F.data == "start")
async def call_start(callback: types.CallbackQuery, session: AsyncSession):
    await handle_start(callback, session)