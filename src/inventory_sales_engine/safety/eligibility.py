from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from uuid import uuid4

from inventory_sales_engine.config import ApprovalMode
from inventory_sales_engine.domain.enums import CampaignState, VerificationStatus
from inventory_sales_engine.domain.models import SendEligibilityDecision
from inventory_sales_engine.safety.counters import DailyCounterStore


@dataclass(frozen=True, slots=True)
class SendEligibilityCommand:
    idempotency_key: str
    mailbox_id: str
    send_date: str
    is_new_email: bool
    outreach_enabled: bool
    emergency_stop: bool
    approval_mode: ApprovalMode
    mailbox_enabled: bool
    campaign_enabled: bool
    campaign_state: CampaignState
    draft_approved: bool
    approval_hash_matches: bool
    first_ten_review_complete: bool
    fit_score: int
    minimum_fit_score: int
    research_confidence: int
    minimum_research_confidence: int
    verification_status: VerificationStatus
    suppressed: bool
    inbound_stop: bool
    cooldown_active: bool
    duplicate: bool
    active_other_campaign: bool
    sequence_step_number: int
    qualified_company_count: int
    max_qualified_companies: int
    budget_available: bool
    sync_healthy: bool
    deliverability_healthy: bool
    max_new_emails_per_day: int
    max_total_emails_per_day: int


class SendEligibilityService:
    def __init__(self, counters: DailyCounterStore) -> None:
        self._counters = counters
        self._reservation_keys: set[str] = set()
        self._lock = RLock()

    def evaluate_and_reserve(self, command: SendEligibilityCommand) -> SendEligibilityDecision:
        with self._lock:
            if command.idempotency_key in self._reservation_keys:
                return SendEligibilityDecision(False, ("duplicate_message",))

            reasons = self._evaluate(command)
            if reasons:
                return SendEligibilityDecision(False, tuple(reasons))

            reserved = self._counters.reserve(
                command.mailbox_id,
                command.send_date,
                is_new=command.is_new_email,
                max_new=command.max_new_emails_per_day,
                max_total=command.max_total_emails_per_day,
            )
            if not reserved:
                return SendEligibilityDecision(False, ("daily_send_limit_reached",))

            self._reservation_keys.add(command.idempotency_key)
            return SendEligibilityDecision(True, reservation_id=str(uuid4()))

    @staticmethod
    def _evaluate(command: SendEligibilityCommand) -> list[str]:
        reasons: list[str] = []
        checks = (
            (not command.outreach_enabled, "outreach_disabled"),
            (command.emergency_stop, "emergency_stop_active"),
            (command.approval_mode is not ApprovalMode.REVIEW, "review_mode_required"),
            (not command.mailbox_enabled, "mailbox_disabled"),
            (not command.campaign_enabled, "campaign_disabled"),
            (command.campaign_state is not CampaignState.RUNNING, "campaign_not_running"),
            (not command.draft_approved, "draft_not_approved"),
            (not command.approval_hash_matches, "approval_hash_mismatch"),
            (not command.first_ten_review_complete, "first_ten_review_incomplete"),
            (command.fit_score < command.minimum_fit_score, "fit_score_below_threshold"),
            (
                command.research_confidence < command.minimum_research_confidence,
                "research_confidence_below_threshold",
            ),
            (command.verification_status is not VerificationStatus.VALID, "email_not_valid"),
            (command.suppressed, "suppressed"),
            (command.inbound_stop, "inbound_stop"),
            (command.cooldown_active, "cooldown_active"),
            (command.duplicate, "duplicate_message"),
            (command.active_other_campaign, "company_in_other_campaign"),
            (command.sequence_step_number > 4, "sequence_limit_exceeded"),
            (
                command.qualified_company_count > command.max_qualified_companies,
                "cohort_limit_exceeded",
            ),
            (not command.budget_available, "budget_exhausted"),
            (not command.sync_healthy, "gmail_sync_unhealthy"),
            (not command.deliverability_healthy, "deliverability_unhealthy"),
        )
        reasons.extend(reason for failed, reason in checks if failed)
        return reasons
