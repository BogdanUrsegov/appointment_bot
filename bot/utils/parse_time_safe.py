from datetime import datetime
from typing import Optional

def parse_time_safe(time_str: str) -> Optional[datetime.time]:
    try:
        return datetime.strptime(time_str.strip(), "%H:%M").time()
    except ValueError:
        return None