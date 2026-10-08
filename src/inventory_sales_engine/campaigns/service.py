from __future__ import annotations

from dataclasses import dataclass, replace

from inventory_sales_engine.domain.enums import CampaignState
from inventory_sales_engine.domain.transitions import transition_campaign_state


class EnrollmentConflict(ValueError):
    pass


class CohortLimitReached(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CampaignRecord:
    id: str
    state: CampaignState = CampaignState.DRAFT


@dataclass(frozen=True, slots=True)
class MembershipRecord:
    campaign_id: str
    company_id: str
    active: bool = True
    stopped_reason: str | None = None


class CampaignService:
    def __init__(self) -> None:
        self._campaigns: dict[str, CampaignRecord] = {}
        self._memberships: dict[tuple[str, str], MembershipRecord] = {}

    def create(self, campaign_id: str) -> CampaignRecord:
        campaign = CampaignRecord(campaign_id)
        self._campaigns[campaign_id] = campaign
        return campaign

    def transition(self, campaign_id: str, target: CampaignState) -> CampaignRecord:
        current = self._campaigns[campaign_id]
        updated = replace(current, state=transition_campaign_state(current.state, target))
        self._campaigns[campaign_id] = updated
        return updated

    def enroll(self, campaign_id: str, company_id: str) -> MembershipRecord:
        if campaign_id not in self._campaigns:
            raise KeyError(campaign_id)
        if any(
            membership.company_id == company_id and membership.active
            for membership in self._memberships.values()
        ):
            raise EnrollmentConflict(f"Company {company_id} already has an active campaign")
        membership = MembershipRecord(campaign_id, company_id)
        self._memberships[(campaign_id, company_id)] = membership
        return membership

    def stop_membership(self, campaign_id: str, company_id: str, *, reason: str) -> MembershipRecord:
        key = (campaign_id, company_id)
        updated = replace(self._memberships[key], active=False, stopped_reason=reason)
        self._memberships[key] = updated
        return updated


class QualificationCohort:
    def __init__(self, *, max_companies: int) -> None:
        if max_companies > 100:
            raise ValueError("MVP cohort ceiling cannot exceed 100")
        self._max_companies = max_companies
        self._company_ids: set[str] = set()

    @property
    def count(self) -> int:
        return len(self._company_ids)

    def add(self, company_id: str) -> bool:
        if company_id in self._company_ids:
            return False
        if self.count >= self._max_companies:
            raise CohortLimitReached("Qualification cohort is full")
        self._company_ids.add(company_id)
        return True

