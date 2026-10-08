from __future__ import annotations

import pytest

from inventory_sales_engine.campaigns.service import CampaignService, EnrollmentConflict
from inventory_sales_engine.domain.enums import CampaignState
from inventory_sales_engine.domain.transitions import InvalidTransition


def test_campaign_uses_domain_transition_rules() -> None:
    service = CampaignService()
    campaign = service.create("campaign-1")

    assert service.transition(campaign.id, CampaignState.RUNNING).state is CampaignState.RUNNING
    assert service.transition(campaign.id, CampaignState.PAUSED).state is CampaignState.PAUSED

    with pytest.raises(InvalidTransition):
        service.transition(campaign.id, CampaignState.COMPLETED)


def test_company_cannot_join_two_active_campaigns() -> None:
    service = CampaignService()
    service.create("campaign-1")
    service.create("campaign-2")
    service.enroll("campaign-1", "company-1")

    with pytest.raises(EnrollmentConflict):
        service.enroll("campaign-2", "company-1")


def test_stopping_membership_allows_later_manual_enrollment() -> None:
    service = CampaignService()
    service.create("campaign-1")
    service.create("campaign-2")
    service.enroll("campaign-1", "company-1")
    service.stop_membership("campaign-1", "company-1", reason="OPERATOR_STOP")

    assert service.enroll("campaign-2", "company-1").active is True

