import os
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from dotenv import load_dotenv

# Загружаем .env один раз при импорте
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Читаем переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

if not all([BOT_TOKEN, REDIS_URL, ADMIN_ID]):
    raise ValueError("Missing required env vars: BOT_TOKEN, REDIS_URL, ADMIN_ID")

# Создаём компоненты
bot = Bot(token=BOT_TOKEN)
redis_client = Redis.from_url(REDIS_URL)
storage = RedisStorage(redis=redis_client)
dp = Dispatcher(storage=storage)

# Экспортируем
__all__ = ["bot", "dp", "ADMIN_ID"]