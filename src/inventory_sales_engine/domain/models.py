from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class SendEligibilityDecision:
    allowed: bool
    reasons: tuple[str, ...] = ()
    reservation_id: str | None = None


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_type: str
    entity_type: str
    entity_id: str
    occurred_at: datetime
    data: dict[str, Any]

