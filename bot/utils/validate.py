# Валидаторы
import re


def validate_name(value: str) -> bool:
    return bool(re.fullmatch(r"[а-яА-ЯёЁa-zA-Z\- ]{2,50}", value))

def validate_age(value: str) -> bool:
    return value.isdigit() and 14 <= int(value) <= 99

def validate_phone(value: str) -> bool:
    return bool(re.fullmatch(r"\+?7\d{10}", re.sub(r"[^\d+]", "", value)))

def validate_time(t: str) -> bool:
    try:
        from datetime import datetime
        datetime.strptime(t, "%H:%M")
        return True
    except ValueError:
        return False

def validate_duration(d: str) -> bool:
    return d.isdigit() and int(d) > 0