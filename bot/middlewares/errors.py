import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError
import traceback
import emoji

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseMiddleware):
    """Миддлварь для обработки ошибок с красивым выводом"""
    
    ERROR_MESSAGES = {
        "database": {
            "title": "🗄️ Проблема с базой данных",
            "message": "К сожалению, произошла ошибка при работе с базой данных. Пожалуйста, попробуйте позже.",
            "emoji": "🗄️"
        },
        "redis": {
            "title": "💾 Проблема с кэшем",
            "message": "Возникла временная проблема с кэшированием данных. Мы уже работаем над решением.",
            "emoji": "💾"
        },
        "network": {
            "title": "🌐 Проблема с сетью",
            "message": "Обнаружены проблемы с сетевым соединением. Проверьте подключение и попробуйте снова.",
            "emoji": "🌐"
        },
        "validation": {
            "title": "⚠️ Ошибка ввода",
            "message": "Пожалуйста, проверьте правильность введенных данных и попробуйте еще раз.",
            "emoji": "⚠️"
        },
        "permission": {
            "title": "🔒 Отказано в доступе",
            "message": "У вас нет прав для выполнения этого действия. Пожалуйста, обратитесь к администратору.",
            "emoji": "🔒"
        },
        "default": {
            "title": "🚨 Неизвестная ошибка",
            "message": "Произошла непредвиденная ошибка. Наши разработчики уже работают над решением проблемы.",
            "emoji": "🚨"
        }
    }

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
            
        except Exception as e:
            return await self.handle_error(event, data, e)

    async def handle_error(
        self, 
        event: TelegramObject, 
        data: Dict[str, Any], 
        error: Exception
    ):
        """Обработка ошибки с красивым сообщением"""
        
        # Определяем тип ошибки
        error_type = self._classify_error(error)
        error_info = self.ERROR_MESSAGES.get(error_type, self.ERROR_MESSAGES["default"])
        
        # Логируем ошибку
        self._log_error(error, error_type)
        
        # Отправляем красивое сообщение пользователю
        await self._send_error_message(event, error_info, error)
        
        # Отправляем детали разработчикам
        await self._notify_developers(event, data, error, error_type)
        
        return None

    def _classify_error(self, error: Exception) -> str:
        """Классификация ошибки"""
        error_str = str(error).lower()
        
        if any(word in error_str for word in ['database', 'postgresql', 'psycopg', 'sql']):
            return "database"
        elif any(word in error_str for word in ['redis', 'cache', 'connection']):
            return "redis"
        elif any(word in error_str for word in ['network', 'timeout', 'connection']):
            return "network"
        elif any(word in error_str for word in ['validation', 'invalid', 'format']):
            return "validation"
        elif any(word in error_str for word in ['permission', 'access', 'denied']):
            return "permission"
        else:
            return "default"

    def _log_error(self, error: Exception, error_type: str):
        """Логирование ошибки"""
        logger.error(
            f"Тип ошибки: {error_type}\n"
            f"Сообщение: {str(error)}\n"
            f"Трассировка:\n{traceback.format_exc()}",
            exc_info=True
        )

    async def _send_error_message(
        self, 
        event: TelegramObject, 
        error_info: Dict[str, str], 
        error: Exception
    ):
        """Отправка красивого сообщения об ошибке пользователю"""
        
        if not isinstance(event, (Message, CallbackQuery)):
            return

        user_message = (
            f"{error_info['emoji']} <b>{error_info['title']}</b>\n\n"
            f"{error_info['message']}\n\n"
            f"🔧 <i>Техническая информация:</i>\n"
            f"• Тип ошибки: <code>{type(error).__name__}</code>\n"
            f"• Время: {self._get_current_time()}\n\n"
            f"💬 Если проблема не решится, пожалуйста, свяжитесь с поддержкой."
        )

        try:
            if isinstance(event, Message):
                await event.answer(user_message, parse_mode="HTML")
            elif isinstance(event, CallbackQuery):
                await event.answer(user_message, show_alert=True, parse_mode="HTML")
        except TelegramAPIError as e:
            logger.error(f"Ошибка отправки сообщения пользователю: {e}")

    async def _notify_developers(
        self, 
        event: TelegramObject, 
        data: Dict[str, Any], 
        error: Exception,
        error_type: str
    ):
        """Уведомление разработчиков о критической ошибке"""
        
        if not isinstance(event, (Message, CallbackQuery)):
            return

        user = data.get("event_from_user")
        if not user:
            return

        # Получаем информацию о событии
        event_info = self._get_event_info(event)
        
        # Формируем сообщение для разработчиков
        dev_message = (
            f"{emoji.emojize(':red_exclamation_mark:')} <b>КРИТИЧЕСКАЯ ОШИБКА</b>\n\n"
            f"{'=' * 40}\n\n"
            f"<b>Информация о пользователе:</b>\n"
            f"👤 Имя: {user.full_name}\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"{'@' + user.username if user.username else 'Нет username'}\n\n"
            f"<b>Информация о событии:</b>\n"
            f"{event_info}\n\n"
            f"<b>Информация об ошибке:</b>\n"
            f"🚨 Тип: <code>{error_type}</code>\n"
            f"❌ Класс: <code>{type(error).__name__}</code>\n"
            f"📄 Сообщение: <code>{str(error)}</code>\n"
            f"🕐 Время: {self._get_current_time()}\n\n"
            f"<b>Трассировка:</b>\n"
            f"<pre>{traceback.format_exc()}</pre>"
        )

        # Отправляем в канал разработчиков
        bot: Bot = data.get("bot")
        dev_chat_id = data.get("developer_chat_id")  # ID чата разработчиков
        
        if bot and dev_chat_id:
            try:
                await bot.send_message(
                    chat_id=dev_chat_id,
                    text=dev_message,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки разработчикам: {e}")

    def _get_event_info(self, event: TelegramObject) -> str:
        """Получение информации о событии"""
        if isinstance(event, Message):
            if event.text:
                return f"💬 Текст: <code>{event.text}</code>"
            elif event.text.startswith('/'):
                return f"🤖 Команда: <code>{event.text}</code>"
        elif isinstance(event, CallbackQuery):
            return f"🔄 Callback: <code>{event.data}</code>"
        return "Неизвестное событие"

    def _get_current_time(self) -> str:
        """Получение текущего времени"""
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%Y %H:%M:%S")