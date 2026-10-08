from __future__ import annotations

from dataclasses import replace

import pytest

from inventory_sales_engine.config import ApprovalMode
from inventory_sales_engine.domain.enums import CampaignState, VerificationStatus
from inventory_sales_engine.safety.counters import DailyCounterStore
from inventory_sales_engine.safety.eligibility import SendEligibilityCommand, SendEligibilityService


def eligible_command() -> SendEligibilityCommand:
    return SendEligibilityCommand(
        idempotency_key="message-1",
        mailbox_id="mailbox-1",
        send_date="2026-08-18",
        is_new_email=True,
        outreach_enabled=True,
        emergency_stop=False,
        approval_mode=ApprovalMode.REVIEW,
        mailbox_enabled=True,
        campaign_enabled=True,
        campaign_state=CampaignState.RUNNING,
        draft_approved=True,
        approval_hash_matches=True,
        first_ten_review_complete=True,
        fit_score=80,
        minimum_fit_score=70,
        research_confidence=85,
        minimum_research_confidence=70,
        verification_status=VerificationStatus.VALID,
        suppressed=False,
        inbound_stop=False,
        cooldown_active=False,
        duplicate=False,
        active_other_campaign=False,
        sequence_step_number=1,
        qualified_company_count=50,
        max_qualified_companies=100,
        budget_available=True,
        sync_healthy=True,
        deliverability_healthy=True,
        max_new_emails_per_day=20,
        max_total_emails_per_day=40,
    )


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"outreach_enabled": False}, "outreach_disabled"),
        ({"emergency_stop": True}, "emergency_stop_active"),
        ({"mailbox_enabled": False}, "mailbox_disabled"),
        ({"campaign_enabled": False}, "campaign_disabled"),
        ({"campaign_state": CampaignState.PAUSED}, "campaign_not_running"),
        ({"draft_approved": False}, "draft_not_approved"),
        ({"approval_hash_matches": False}, "approval_hash_mismatch"),
        ({"first_ten_review_complete": False}, "first_ten_review_incomplete"),
        ({"fit_score": 69}, "fit_score_below_threshold"),
        ({"research_confidence": 69}, "research_confidence_below_threshold"),
        ({"verification_status": VerificationStatus.UNKNOWN}, "email_not_valid"),
        ({"verification_status": VerificationStatus.ACCEPT_ALL}, "email_not_valid"),
        ({"suppressed": True}, "suppressed"),
        ({"inbound_stop": True}, "inbound_stop"),
        ({"cooldown_active": True}, "cooldown_active"),
        ({"duplicate": True}, "duplicate_message"),
        ({"active_other_campaign": True}, "company_in_other_campaign"),
        ({"sequence_step_number": 5}, "sequence_limit_exceeded"),
        ({"qualified_company_count": 101}, "cohort_limit_exceeded"),
        ({"budget_available": False}, "budget_exhausted"),
        ({"sync_healthy": False}, "gmail_sync_unhealthy"),
        ({"deliverability_healthy": False}, "deliverability_unhealthy"),
    ],
)
def test_each_safety_gate_fails_closed(changes: dict, reason: str) -> None:
    service = SendEligibilityService(DailyCounterStore())

    decision = service.evaluate_and_reserve(replace(eligible_command(), **changes))

    assert decision.allowed is False
    assert reason in decision.reasons


def test_eligible_send_reserves_capacity_and_idempotency_key() -> None:
    service = SendEligibilityService(DailyCounterStore())

    first = service.evaluate_and_reserve(eligible_command())
    second = service.evaluate_and_reserve(eligible_command())

    assert first.allowed is True
    assert first.reservation_id is not None
    assert second.allowed is False
    assert second.reasons == ("duplicate_message",)


def test_daily_capacity_is_checked_at_reservation_time() -> None:
    counters = DailyCounterStore()
    service = SendEligibilityService(counters)
    command = replace(eligible_command(), max_new_emails_per_day=1, max_total_emails_per_day=1)

    assert service.evaluate_and_reserve(command).allowed is True
    blocked = service.evaluate_and_reserve(replace(command, idempotency_key="message-2"))

    assert blocked.allowed is False
    assert blocked.reasons == ("daily_send_limit_reached",)

