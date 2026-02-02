# bot/utils/user_checker.py
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from bot.database.models import User


def check_user_profile_completion(user: User) -> Dict[str, bool]:
    """
    Проверяет, заполнены ли обязательные поля профиля пользователя.
    
    Args:
        user: Объект пользователя
        
    Returns:
        Dict с результатами проверки каждого поля и общим статусом
    """
    # Определяем, какие поля считаем важными для профиля
    important_fields = [
        ('first_name', 'Имя', bool(user.first_name)),
        ('last_name', 'Фамилия', bool(user.last_name)),
        ('age', 'Возраст', bool(user.age)),
        ('phone', 'Телефон', bool(user.phone)),
    ]
    
    # Собираем результат
    result = {
        'is_complete': True,
        'missing_fields': [],
        'fields': {}
    }
    
    for field_key, field_name, is_filled in important_fields:
        result['fields'][field_key] = {
            'name': field_name,
            'is_filled': is_filled,
            'value': getattr(user, field_key, None)
        }
        
        if not is_filled:
            result['is_complete'] = False
            result['missing_fields'].append(field_key)
    
    return result


def get_profile_completion_message(user: User) -> str:
    """
    Формирует сообщение о заполнении профиля.
    
    Args:
        user: Объект пользователя
        
    Returns:
        Текст сообщения для пользователя
    """
    check_result = check_user_profile_completion(user)
    
    if check_result['is_complete']:
        # Профиль полностью заполнен
        message = "✅ Ваш профиль полностью заполнен!\n\n"
        message += f"👤 Имя: {user.first_name}\n"
        message += f"👤 Фамилия: {user.last_name}\n"
        if user.patronymic:
            message += f"👤 Отчество: {user.patronymic}\n"
        if user.phone:
            message += f"📱 Телефон: {user.phone}\n"
        if user.email:
            message += f"📧 Email: {user.email}\n"
        message += f"📅 Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}"
    else:
        # Профиль не заполнен
        message = "⚠️ Ваш профиль заполнен не полностью.\n\n"
        message += "Чтобы пользоваться ботом, пожалуйста, заполните недостающие данные:\n"
        
        for field_key in check_result['missing_fields']:
            field_info = check_result['fields'][field_key]
            message += f"❌ {field_info['name']}\n"
        
        message += "\nНажмите кнопку 'Редактировать профиль', чтобы заполнить недостающие данные."
    
    return message


def get_profile_edit_keyboard(check_result: Dict) -> Dict[str, str]:
    """
    Создает клавиатуру для редактирования профиля.
    
    Args:
        check_result: Результат проверки профиля
        
    Returns:
        Dict с данными для клавиатуры
    """
    buttons = []
    
    if not check_result['is_complete']:
        # Предлагаем заполнить недостающие поля
        for field_key in check_result['missing_fields']:
            field_info = check_result['fields'][field_key]
            callback_data = f"edit_{field_key}"
            buttons.append({
                'text': f"✏️ {field_info['name']}",
                'callback_data': callback_data
            })
    
    # Всегда добавляем кнопки для редактирования всех полей
    all_fields = [
        ('first_name', 'Имя'),
        ('last_name', 'Фамилия'),
        ('patronymic', 'Отчество'),
        ('phone', 'Телефон'),
        ('email', 'Email')
    ]
    
    for field_key, field_name in all_fields:
        callback_data = f"edit_{field_key}"
        current_value = check_result['fields'].get(field_key, {}).get('value', 'Не заполнено')
        
        buttons.append({
            'text': f"📝 {field_name}: {current_value[:15] if current_value else '❌'}",
            'callback_data': callback_data
        })
    
    # Кнопка для завершения
    if check_result['is_complete']:
        buttons.append({
            'text': "✅ Профиль заполнен",
            'callback_data': "profile_complete"
        })
    
    return {
        'inline_keyboard': [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    }