from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from inventory_sales_engine.safety.counters import DailyCounterStore
from inventory_sales_engine.safety.eligibility import SendEligibilityService
from tests.safety.test_send_eligibility import eligible_command


def test_concurrent_reservations_cannot_exceed_daily_cap() -> None:
    service = SendEligibilityService(DailyCounterStore())
    commands = [
        replace(
            eligible_command(),
            idempotency_key=f"message-{index}",
            max_new_emails_per_day=5,
            max_total_emails_per_day=5,
        )
        for index in range(25)
    ]

    with ThreadPoolExecutor(max_workers=10) as executor:
        decisions = list(executor.map(service.evaluate_and_reserve, commands))

    assert sum(decision.allowed for decision in decisions) == 5


def test_concurrent_duplicate_key_allows_only_one_reservation() -> None:
    service = SendEligibilityService(DailyCounterStore())

    with ThreadPoolExecutor(max_workers=10) as executor:
        decisions = list(executor.map(service.evaluate_and_reserve, [eligible_command()] * 20))

    assert sum(decision.allowed for decision in decisions) == 1
