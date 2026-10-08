from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from inventory_sales_engine.domain.enums import (
    CampaignState,
    LeadStage,
    MessageState,
    ReplyClass,
    StopReason,
    VerificationStatus,
)
from inventory_sales_engine.domain.models import SendEligibilityDecision
from inventory_sales_engine.domain.transitions import (
    InvalidTransition,
    transition_campaign_state,
    transition_lead_stage,
)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (LeadStage.DISCOVERED, LeadStage.RESEARCHED),
        (LeadStage.RESEARCHED, LeadStage.QUALIFIED),
        (LeadStage.QUALIFIED, LeadStage.CONTACT_FOUND),
        (LeadStage.CONTACT_FOUND, LeadStage.VERIFIED),
        (LeadStage.VERIFIED, LeadStage.READY_TO_SEND),
        (LeadStage.READY_TO_SEND, LeadStage.CONTACTED),
        (LeadStage.CONTACTED, LeadStage.FOLLOW_UP),
        (LeadStage.FOLLOW_UP, LeadStage.REPLIED),
        (LeadStage.REPLIED, LeadStage.INTERESTED),
        (LeadStage.INTERESTED, LeadStage.DEMO_BOOKED),
        (LeadStage.DEMO_BOOKED, LeadStage.PILOT),
        (LeadStage.PILOT, LeadStage.CUSTOMER),
        (LeadStage.CONTACTED, LeadStage.UNSUBSCRIBED),
        (LeadStage.REPLIED, LeadStage.LOST),
    ],
)
def test_valid_lead_stage_transitions(current: LeadStage, target: LeadStage) -> None:
    assert transition_lead_stage(current, target) is target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (LeadStage.DISCOVERED, LeadStage.QUALIFIED),
        (LeadStage.RESEARCHED, LeadStage.CONTACT_FOUND),
        (LeadStage.CUSTOMER, LeadStage.CONTACTED),
        (LeadStage.LOST, LeadStage.RESEARCHED),
        (LeadStage.UNSUBSCRIBED, LeadStage.READY_TO_SEND),
        (LeadStage.REPLIED, LeadStage.FOLLOW_UP),
    ],
)
def test_invalid_or_terminal_lead_stage_transitions_fail(
    current: LeadStage, target: LeadStage
) -> None:
    with pytest.raises(InvalidTransition):
        transition_lead_stage(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (CampaignState.DRAFT, CampaignState.RUNNING),
        (CampaignState.RUNNING, CampaignState.PAUSED),
        (CampaignState.PAUSED, CampaignState.RUNNING),
        (CampaignState.RUNNING, CampaignState.COMPLETED),
        (CampaignState.DRAFT, CampaignState.STOPPED),
        (CampaignState.PAUSED, CampaignState.STOPPED),
    ],
)
def test_valid_campaign_transitions(current: CampaignState, target: CampaignState) -> None:
    assert transition_campaign_state(current, target) is target


@pytest.mark.parametrize("terminal", [CampaignState.STOPPED, CampaignState.COMPLETED])
def test_terminal_campaigns_cannot_reopen(terminal: CampaignState) -> None:
    with pytest.raises(InvalidTransition):
        transition_campaign_state(terminal, CampaignState.RUNNING)


def test_domain_enums_expose_only_approved_values() -> None:
    assert {status.value for status in VerificationStatus} == {
        "VALID",
        "INVALID",
        "ACCEPT_ALL",
        "UNKNOWN",
    }
    assert ReplyClass.UNSUBSCRIBE.value == "UNSUBSCRIBE"
    assert StopReason.INBOUND_HUMAN.value == "INBOUND_HUMAN"
    assert MessageState.UNKNOWN_SEND_STATE.value == "UNKNOWN_SEND_STATE"


def test_send_decisions_are_immutable() -> None:
    decision = SendEligibilityDecision(allowed=False, reasons=("suppressed",))

    with pytest.raises(FrozenInstanceError):
        decision.allowed = True  # type: ignore[misc]
