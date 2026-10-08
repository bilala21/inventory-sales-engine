from __future__ import annotations

from email import policy
from email.parser import BytesParser

from inventory_sales_engine.mail.service import ComplianceIdentity, build_mime_message


def identity() -> ComplianceIdentity:
    return ComplianceIdentity(
        sender_name="Bilal",
        sender_email="bilal@example.com",
        physical_postal_address="123 Main St, Chicago, IL 60601",
        unsubscribe_url="https://example.com/unsubscribe/token",
    )


def parse(raw: bytes):
    return BytesParser(policy=policy.default).parsebytes(raw)


def test_initial_message_has_accurate_compliance_and_unsubscribe_headers() -> None:
    raw = build_mime_message(
        identity=identity(),
        recipient="sara@packaging.example",
        subject="Inventory checking",
        body="Hi Sara,\n\nWorth a quick demo?",
        message_id="<stable-1@example.com>",
    )
    message = parse(raw)

    assert message["From"] == "Bilal <bilal@example.com>"
    assert message["To"] == "sara@packaging.example"
    assert message["Message-ID"] == "<stable-1@example.com>"
    assert message["List-Unsubscribe"] == "<https://example.com/unsubscribe/token>"
    assert message["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"
    body = message.get_body(preferencelist=("plain",)).get_content()
    assert "123 Main St, Chicago, IL 60601" in body
    assert "reply unsubscribe" in body.casefold()
    assert "commercial outreach" in body.casefold()


def test_follow_up_stays_in_same_rfc_thread() -> None:
    message = parse(
        build_mime_message(
            identity=identity(),
            recipient="sara@packaging.example",
            subject="Re: Inventory checking",
            body="Hi Sara,\n\nFollowing up.",
            message_id="<stable-2@example.com>",
            in_reply_to="<stable-1@example.com>",
            references=("<stable-1@example.com>",),
        )
    )

    assert message["In-Reply-To"] == "<stable-1@example.com>"
    assert message["References"] == "<stable-1@example.com>"


def test_missing_physical_address_blocks_mime_creation() -> None:
    incomplete = ComplianceIdentity("Bilal", "bilal@example.com", "", "https://example.com/u")

    try:
        build_mime_message(
            identity=incomplete,
            recipient="sara@example.com",
            subject="Hello",
            body="Body",
            message_id="<id@example.com>",
        )
    except ValueError as error:
        assert "postal" in str(error)
    else:
        raise AssertionError("Missing address must fail closed")
