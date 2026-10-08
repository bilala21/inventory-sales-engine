from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from inventory_sales_engine.domain.enums import LeadStage
from inventory_sales_engine.domain.transitions import transition_lead_stage


@dataclass(frozen=True, slots=True)
class CrmStageEvent:
    company_id: str
    stage: LeadStage
    actor: str
    occurred_at: datetime


class CrmService:
    def __init__(self) -> None:
        self._events: dict[str, list[CrmStageEvent]] = {}

    def create_lead(self, company_id: str, *, actor: str = "discovery") -> CrmStageEvent:
        if company_id in self._events:
            raise ValueError("Lead already exists")
        event = CrmStageEvent(company_id, LeadStage.DISCOVERED, actor, datetime.now(timezone.utc))
        self._events[company_id] = [event]
        return event

    def transition(self, company_id: str, target: LeadStage, *, actor: str) -> CrmStageEvent:
        current = self.current_stage(company_id)
        stage = transition_lead_stage(current, target)
        event = CrmStageEvent(company_id, stage, actor, datetime.now(timezone.utc))
        self._events[company_id].append(event)
        return event

    def timeline(self, company_id: str) -> tuple[CrmStageEvent, ...]:
        return tuple(self._events[company_id])

    def current_stage(self, company_id: str) -> LeadStage:
        return self._events[company_id][-1].stage

