from __future__ import annotations

from inventory_sales_engine.domain.enums import CampaignState, LeadStage


class InvalidTransition(ValueError):
    pass


_LEAD_TRANSITIONS: dict[LeadStage, frozenset[LeadStage]] = {
    LeadStage.DISCOVERED: frozenset({LeadStage.RESEARCHED, LeadStage.LOST}),
    LeadStage.RESEARCHED: frozenset({LeadStage.QUALIFIED, LeadStage.LOST}),
    LeadStage.QUALIFIED: frozenset({LeadStage.CONTACT_FOUND, LeadStage.LOST}),
    LeadStage.CONTACT_FOUND: frozenset({LeadStage.VERIFIED, LeadStage.LOST}),
    LeadStage.VERIFIED: frozenset({LeadStage.READY_TO_SEND, LeadStage.LOST}),
    LeadStage.READY_TO_SEND: frozenset(
        {LeadStage.CONTACTED, LeadStage.LOST, LeadStage.UNSUBSCRIBED}
    ),
    LeadStage.CONTACTED: frozenset(
        {LeadStage.FOLLOW_UP, LeadStage.REPLIED, LeadStage.LOST, LeadStage.UNSUBSCRIBED}
    ),
    LeadStage.FOLLOW_UP: frozenset(
        {LeadStage.REPLIED, LeadStage.LOST, LeadStage.UNSUBSCRIBED}
    ),
    LeadStage.REPLIED: frozenset(
        {LeadStage.INTERESTED, LeadStage.LOST, LeadStage.UNSUBSCRIBED}
    ),
    LeadStage.INTERESTED: frozenset(
        {LeadStage.DEMO_BOOKED, LeadStage.LOST, LeadStage.UNSUBSCRIBED}
    ),
    LeadStage.DEMO_BOOKED: frozenset({LeadStage.PILOT, LeadStage.LOST}),
    LeadStage.PILOT: frozenset({LeadStage.CUSTOMER, LeadStage.LOST}),
    LeadStage.CUSTOMER: frozenset(),
    LeadStage.LOST: frozenset(),
    LeadStage.UNSUBSCRIBED: frozenset(),
}

_CAMPAIGN_TRANSITIONS: dict[CampaignState, frozenset[CampaignState]] = {
    CampaignState.DRAFT: frozenset({CampaignState.RUNNING, CampaignState.STOPPED}),
    CampaignState.RUNNING: frozenset(
        {CampaignState.PAUSED, CampaignState.STOPPED, CampaignState.COMPLETED}
    ),
    CampaignState.PAUSED: frozenset({CampaignState.RUNNING, CampaignState.STOPPED}),
    CampaignState.STOPPED: frozenset(),
    CampaignState.COMPLETED: frozenset(),
}


def transition_lead_stage(current: LeadStage, target: LeadStage) -> LeadStage:
    if target not in _LEAD_TRANSITIONS[current]:
        raise InvalidTransition(f"Lead stage cannot transition from {current} to {target}")
    return target


def transition_campaign_state(current: CampaignState, target: CampaignState) -> CampaignState:
    if target not in _CAMPAIGN_TRANSITIONS[current]:
        raise InvalidTransition(f"Campaign cannot transition from {current} to {target}")
    return target
