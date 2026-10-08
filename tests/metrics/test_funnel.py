from __future__ import annotations

from inventory_sales_engine.domain.enums import LeadStage
from inventory_sales_engine.metrics.service import (
    VALIDATION_TARGETS,
    LeadOutcome,
    calculate_funnel,
)


def test_funnel_and_business_rates_are_hand_derived() -> None:
    outcomes = [
        LeadOutcome(LeadStage.CUSTOMER, delivered=True, meaningful_conversation=True),
        LeadOutcome(LeadStage.PILOT, delivered=True, meaningful_conversation=True),
        LeadOutcome(LeadStage.DEMO_BOOKED, delivered=True, meaningful_conversation=True),
        LeadOutcome(LeadStage.INTERESTED, delivered=True, meaningful_conversation=True),
        LeadOutcome(LeadStage.REPLIED, delivered=True, meaningful_conversation=False),
        LeadOutcome(LeadStage.CONTACTED, delivered=False, meaningful_conversation=False),
    ]

    metrics = calculate_funnel(outcomes)

    assert metrics.found == 6
    assert metrics.contacted == 6
    assert metrics.delivered == 5
    assert metrics.replied == 5
    assert metrics.meaningful_conversations == 4
    assert metrics.demos == 3
    assert metrics.pilots == 2
    assert metrics.customers == 1
    assert metrics.positive_reply_rate == 0.8
    assert metrics.demo_rate == 0.6


def test_validation_targets_are_recorded_as_targets_not_guarantees() -> None:
    assert VALIDATION_TARGETS == {
        "qualified_companies": 100,
        "delivered_targeted_emails": 50,
        "meaningful_conversations": 5,
        "demos": 3,
        "paid_pilots": 1,
    }

