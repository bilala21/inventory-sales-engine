from __future__ import annotations

import pytest
from pydantic import ValidationError

from inventory_sales_engine.config import ApprovalMode, Settings


def test_defaults_disable_outreach_and_require_review_mode() -> None:
    settings = Settings(_env_file=None)

    assert settings.outreach_enabled is False
    assert settings.emergency_stop is True
    assert settings.approval_mode is ApprovalMode.REVIEW
    assert settings.max_new_emails_per_day == 20
    assert settings.max_total_emails_per_day == 40
    assert settings.max_qualified_companies == 100


def test_malformed_outreach_boolean_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OUTREACH_ENABLED", "sometimes")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


@pytest.mark.parametrize("mode", ["CONTROLLED_AUTO", "FULL_AUTO"])
def test_non_review_approval_modes_are_rejected(mode: str) -> None:
    with pytest.raises(ValidationError):
        Settings(approval_mode=mode, _env_file=None)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("max_new_emails_per_day", 21),
        ("max_total_emails_per_day", 41),
        ("max_qualified_companies", 101),
    ],
)
def test_mvp_caps_cannot_exceed_approved_ceilings(field: str, value: int) -> None:
    with pytest.raises(ValidationError):
        Settings(**{field: value}, _env_file=None)


def test_send_readiness_requires_identity_address_and_booking_link() -> None:
    settings = Settings(
        outreach_enabled=True,
        emergency_stop=False,
        sender_name="Bilal",
        sender_email="bilal@example.com",
        physical_postal_address="",
        booking_link="https://example.com/book",
        _env_file=None,
    )

    assert settings.send_readiness_errors() == ("physical_postal_address_missing",)

