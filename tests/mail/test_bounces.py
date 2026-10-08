from __future__ import annotations

from inventory_sales_engine.mail.inbound_sync import BounceDisposition, parse_bounce


def test_delivery_status_failure_is_a_hard_bounce_stop() -> None:
    body = "Final-Recipient: rfc822; bad@example.com\nAction: failed\nStatus: 5.1.1"

    result = parse_bounce("Delivery Status Notification (Failure)", body)

    assert result.disposition is BounceDisposition.HARD_BOUNCE
    assert result.recipient == "bad@example.com"


def test_ambiguous_bounce_like_message_stops_for_review() -> None:
    result = parse_bounce("Undeliverable", "We could not complete delivery.")

    assert result.disposition is BounceDisposition.AMBIGUOUS_STOP


def test_normal_reply_is_not_a_bounce() -> None:
    result = parse_bounce("Re: Inventory checking", "Yes, please send details.")

    assert result.disposition is BounceDisposition.NOT_BOUNCE
