from __future__ import annotations

from datetime import datetime, timedelta


SEQUENCE_BUSINESS_DAY_OFFSETS = (0, 3, 5, 7)


def _add_business_days(start: datetime, offset: int) -> datetime:
    current = start
    remaining = offset
    while remaining:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


def sequence_send_times(start: datetime) -> tuple[datetime, ...]:
    if start.tzinfo is None or start.utcoffset() is None:
        raise ValueError("start must be timezone-aware")
    return tuple(_add_business_days(start, offset) for offset in SEQUENCE_BUSINESS_DAY_OFFSETS)

