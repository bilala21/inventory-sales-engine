from __future__ import annotations

from inventory_sales_engine.crm.service import CrmService
from inventory_sales_engine.domain.enums import LeadStage


def test_crm_timeline_is_append_only_and_derives_current_stage() -> None:
    crm = CrmService()
    crm.create_lead("company-1")
    crm.transition("company-1", LeadStage.RESEARCHED, actor="system")
    crm.transition("company-1", LeadStage.QUALIFIED, actor="qualification-policy-v1")

    timeline = crm.timeline("company-1")

    assert [event.stage for event in timeline] == [
        LeadStage.DISCOVERED,
        LeadStage.RESEARCHED,
        LeadStage.QUALIFIED,
    ]
    assert crm.current_stage("company-1") is LeadStage.QUALIFIED
    assert isinstance(timeline, tuple)

