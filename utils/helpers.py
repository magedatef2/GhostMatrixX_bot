"""
Small helper utilities.
"""
from datetime import datetime, timedelta


def now() -> datetime:
    return datetime.utcnow()


def hours_from_now(hours: int) -> datetime:
    return now() + timedelta(hours=hours)


def format_egp(amount: int) -> str:
    return f"{amount} جنيه"


def mask_number(number: str) -> str:
    if len(number) < 4:
        return number
    return number[:4] + "*" * (len(number) - 6) + number[-2:]
