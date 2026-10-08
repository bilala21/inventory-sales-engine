from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from inventory_sales_engine.campaigns.scheduling import sequence_send_times


def test_sequence_uses_zero_three_five_seven_business_day_offsets() -> None:
    start = datetime(2026, 8, 21, 9, 30, tzinfo=ZoneInfo("America/Chicago"))  # Friday

    sends = sequence_send_times(start)

    assert [item.date().isoformat() for item in sends] == [
        "2026-08-21",
        "2026-08-26",
        "2026-08-28",
        "2026-09-01",
    ]
    assert all(item.hour == 9 and item.minute == 30 for item in sends)


def test_sequence_never_exceeds_four_messages() -> None:
    start = datetime(2026, 8, 18, 9, 0, tzinfo=ZoneInfo("America/Chicago"))

    assert len(sequence_send_times(start)) == 4


def test_naive_datetime_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone"):
        sequence_send_times(datetime(2026, 8, 18, 9, 0))

