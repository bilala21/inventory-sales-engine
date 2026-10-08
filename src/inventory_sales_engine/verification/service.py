from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from inventory_sales_engine.domain.enums import VerificationStatus


@dataclass(frozen=True, slots=True)
class VerificationResult:
    status: VerificationStatus
    provider: str
    checked_at: datetime
    expires_at: datetime | None
    provider_reference: str | None = None


class VerificationProvider(Protocol):
    def verify(self, email: str) -> VerificationResult: ...


def is_send_eligible(result: VerificationResult, *, now: datetime) -> bool:
    return (
        result.status is VerificationStatus.VALID
        and result.expires_at is not None
        and result.checked_at <= now < result.expires_at
    )

