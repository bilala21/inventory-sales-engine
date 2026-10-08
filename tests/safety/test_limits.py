from __future__ import annotations

from inventory_sales_engine.safety.counters import DailyCounterStore


def test_new_email_reservation_increments_new_and_total() -> None:
    store = DailyCounterStore()

    assert store.reserve("mailbox", "2026-08-18", is_new=True, max_new=20, max_total=40)
    assert store.snapshot("mailbox", "2026-08-18") == (1, 1)


def test_follow_up_only_increments_total() -> None:
    store = DailyCounterStore()

    assert store.reserve("mailbox", "2026-08-18", is_new=False, max_new=20, max_total=40)
    assert store.snapshot("mailbox", "2026-08-18") == (0, 1)


def test_daily_caps_fail_without_incrementing() -> None:
    store = DailyCounterStore()
    for _ in range(2):
        assert store.reserve("mailbox", "2026-08-18", is_new=True, max_new=2, max_total=2)

    assert store.reserve("mailbox", "2026-08-18", is_new=True, max_new=2, max_total=2) is False
    assert store.snapshot("mailbox", "2026-08-18") == (2, 2)

