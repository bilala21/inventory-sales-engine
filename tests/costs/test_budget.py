from __future__ import annotations

from datetime import date

import pytest

from inventory_sales_engine.costs.service import CostLedger, MonthlyBudgetExceeded


def test_provider_cost_must_be_preauthorized_before_call() -> None:
    ledger = CostLedger(monthly_budget_usd=1.00)
    authorization = ledger.preauthorize("google_places", "text_search", 0.04, on=date(2026, 8, 18))
    ledger.record(authorization, actual_cost_usd=0.03)

    assert ledger.monthly_cost(date(2026, 8, 31)) == pytest.approx(0.03)


def test_discovery_pauses_before_call_that_exceeds_budget() -> None:
    ledger = CostLedger(monthly_budget_usd=0.05)
    ledger.preauthorize("google_places", "text_search", 0.04, on=date(2026, 8, 18))

    with pytest.raises(MonthlyBudgetExceeded):
        ledger.preauthorize("google_places", "text_search", 0.02, on=date(2026, 8, 18))


def test_cost_per_outcome_is_none_until_outcome_exists() -> None:
    ledger = CostLedger(monthly_budget_usd=10)
    authorization = ledger.preauthorize("llm", "research", 1.0, on=date(2026, 8, 18))
    ledger.record(authorization, actual_cost_usd=1.0)

    assert ledger.cost_per(0, on=date(2026, 8, 18)) is None
    assert ledger.cost_per(2, on=date(2026, 8, 18)) == pytest.approx(0.5)

