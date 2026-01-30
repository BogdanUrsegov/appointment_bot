import logging
import os
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from bot.database.session import init_db
from asyncpg import create_pool

# Импорты проекта
from .create_bot import bot, dp, ADMIN_ID
from .handlers import router

WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
BASE_URL = os.getenv("WEBHOOK_BASE_URL")
HOST = os.getenv("WEBHOOK_HOST")
PORT = int(os.getenv("WEBHOOK_PORT", 8000))

if not BASE_URL:
    raise ValueError("WEBHOOK_BASE_URL is required")

async def on_startup() -> None:
    # Инициализация БД
    await init_db()
    logging.info("✅ Database tables initialized")

    await bot.set_webhook(f"{BASE_URL}{WEBHOOK_PATH}")
    await bot.send_message(chat_id=ADMIN_ID, text="✅ Бот запущен!")


async def on_shutdown() -> None:
    await bot.send_message(chat_id=ADMIN_ID, text="🛑 Бот остановлен!")
    await bot.delete_webhook(drop_pending_updates=True)


def main() -> None:
    dp.include_router(router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    main()