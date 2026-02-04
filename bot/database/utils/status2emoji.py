def status2emoji(status: str) -> str:
    status_mapping = {
        "scheduled": "🕒",
        "completed": "✅",
        "cancelled": "❌",
        "no_show": "⚠️"
    }
    status_lower = status.lower()
    for key, emoji in status_mapping.items():
        if key in status_lower:
            return emoji
    return "❓"