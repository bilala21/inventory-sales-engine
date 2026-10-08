from __future__ import annotations

from inventory_sales_engine.providers.gmail import GMAIL_OAUTH_SCOPES, OAuthSecret


def test_gmail_oauth_uses_only_required_send_and_read_scopes() -> None:
    assert GMAIL_OAUTH_SCOPES == (
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.readonly",
    )


def test_oauth_secret_never_appears_in_repr_or_str() -> None:
    secret = OAuthSecret("super-secret-refresh-token")

    assert "super-secret" not in repr(secret)
    assert "super-secret" not in str(secret)
    assert str(secret) == "**********"
