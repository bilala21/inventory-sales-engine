from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from inventory_sales_engine.domain.enums import VerificationStatus
from inventory_sales_engine.verification.service import VerificationResult, is_send_eligible


@pytest.mark.parametrize(
    ("status", "allowed"),
    [
        (VerificationStatus.VALID, True),
        (VerificationStatus.INVALID, False),
        (VerificationStatus.ACCEPT_ALL, False),
        (VerificationStatus.UNKNOWN, False),
    ],
)
def test_only_valid_verification_is_send_eligible(
    status: VerificationStatus, allowed: bool
) -> None:
    now = datetime.now(timezone.utc)
    result = VerificationResult(status, "provider", now, now + timedelta(days=7))

    assert is_send_eligible(result, now=now) is allowed


def test_stale_valid_verification_is_blocked() -> None:
    now = datetime.now(timezone.utc)
    result = VerificationResult(
        VerificationStatus.VALID,
        "provider",
        now - timedelta(days=31),
        now - timedelta(seconds=1),
    )

    assert is_send_eligible(result, now=now) is False


def test_missing_expiry_fails_closed() -> None:
    now = datetime.now(timezone.utc)
    result = VerificationResult(VerificationStatus.VALID, "provider", now, None)

    assert is_send_eligible(result, now=now) is False

