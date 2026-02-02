# Валидаторы
import re


def validate_name(value: str) -> bool:
    return bool(re.fullmatch(r"[а-яА-ЯёЁa-zA-Z\- ]{2,50}", value))

def validate_age(value: str) -> bool:
    return value.isdigit() and 14 <= int(value) <= 99

def validate_phone(value: str) -> bool:
    return bool(re.fullmatch(r"\+?7\d{10}", re.sub(r"[^\d+]", "", value)))