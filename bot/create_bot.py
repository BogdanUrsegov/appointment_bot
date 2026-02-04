import os
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from bot.database.session import AsyncSessionLocal
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.logging import ChannelLoggerMiddleware

# Читаем переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
ADMIN_ID = os.getenv("ADMIN_ID")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

if not all([BOT_TOKEN, REDIS_URL, ADMIN_ID]):
    raise ValueError("Missing required env vars: BOT_TOKEN, REDIS_URL, ADMIN_ID")

# Создаём компоненты
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
redis_client = Redis.from_url(REDIS_URL)
storage = RedisStorage(redis=redis_client)
dp = Dispatcher(storage=storage)
dp["session_maker"] = AsyncSessionLocal

dp.update.middleware(DbSessionMiddleware(AsyncSessionLocal))
dp.update.middleware(ChannelLoggerMiddleware(channel_id=LOG_CHANNEL_ID))

# Экспортируем
__all__ = ["bot", "dp", "ADMIN_ID"]