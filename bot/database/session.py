# bot/database/session.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

from .models import Base

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment")

# Асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False,               # включи True для отладки SQL
    pool_size=5,
    max_overflow=10,
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

async def init_db():
    """Создаёт таблицы, если их нет."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)