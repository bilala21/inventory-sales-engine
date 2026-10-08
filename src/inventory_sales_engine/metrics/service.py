from __future__ import annotations

from dataclasses import dataclass

from inventory_sales_engine.domain.enums import LeadStage


VALIDATION_TARGETS = {
    "qualified_companies": 100,
    "delivered_targeted_emails": 50,
    "meaningful_conversations": 5,
    "demos": 3,
    "paid_pilots": 1,
}

STAGE_ORDER = {
    LeadStage.DISCOVERED: 0,
    LeadStage.RESEARCHED: 1,
    LeadStage.QUALIFIED: 2,
    LeadStage.CONTACT_FOUND: 3,
    LeadStage.VERIFIED: 4,
    LeadStage.READY_TO_SEND: 5,
    LeadStage.CONTACTED: 6,
    LeadStage.FOLLOW_UP: 7,
    LeadStage.REPLIED: 8,
    LeadStage.INTERESTED: 9,
    LeadStage.DEMO_BOOKED: 10,
    LeadStage.PILOT: 11,
    LeadStage.CUSTOMER: 12,
    LeadStage.LOST: -1,
    LeadStage.UNSUBSCRIBED: -1,
}


@dataclass(frozen=True, slots=True)
class LeadOutcome:
    stage: LeadStage
    delivered: bool
    meaningful_conversation: bool


@dataclass(frozen=True, slots=True)
class FunnelMetrics:
    found: int
    qualified: int
    contacted: int
    delivered: int
    replied: int
    meaningful_conversations: int
    demos: int
    pilots: int
    customers: int
    positive_reply_rate: float
    demo_rate: float


def calculate_funnel(outcomes: list[LeadOutcome]) -> FunnelMetrics:
    count_at = lambda stage: sum(STAGE_ORDER[item.stage] >= STAGE_ORDER[stage] for item in outcomes)
    delivered = sum(item.delivered for item in outcomes)
    meaningful = sum(item.meaningful_conversation for item in outcomes)
    return FunnelMetrics(
        found=len(outcomes),
        qualified=count_at(LeadStage.QUALIFIED),
        contacted=count_at(LeadStage.CONTACTED),
        delivered=delivered,
        replied=count_at(LeadStage.REPLIED),
        meaningful_conversations=meaningful,
        demos=count_at(LeadStage.DEMO_BOOKED),
        pilots=count_at(LeadStage.PILOT),
        customers=count_at(LeadStage.CUSTOMER),
        positive_reply_rate=meaningful / delivered if delivered else 0.0,
        demo_rate=count_at(LeadStage.DEMO_BOOKED) / delivered if delivered else 0.0,
    )

