from __future__ import annotations

from datetime import datetime, timedelta, timezone

from inventory_sales_engine.mail.inbound_sync import HistoryGap, InboundEvent, InboundSyncState


def event(event_id: str = "event-1") -> InboundEvent:
    return InboundEvent(event_id, "gmail-1", datetime.now(timezone.utc), "buyer@example.com")


def test_duplicate_provider_notification_is_idempotent() -> None:
    state = InboundSyncState(history_id="10")

    assert state.ingest(event()) is True
    assert state.ingest(event()) is False
    assert len(state.messages) == 1


def test_expired_watch_marks_sync_unhealthy() -> None:
    state = InboundSyncState(
        history_id="10", watch_expires_at=datetime.now(timezone.utc) - timedelta(seconds=1)
    )

    assert state.is_healthy(now=datetime.now(timezone.utc)) is False


def test_history_gap_fails_closed_until_all_mail_sweep() -> None:
    state = InboundSyncState(history_id="10")
    state.mark_history_gap(HistoryGap("history 404"))

    assert state.is_healthy(now=datetime.now(timezone.utc)) is False
    state.recover_with_all_mail_sweep([event("event-recovered")], new_history_id="20")
    assert state.is_healthy(now=datetime.now(timezone.utc)) is True
    assert "event-recovered" in state.messages


def test_delayed_events_are_still_ingested() -> None:
    delayed = InboundEvent(
        "late", "gmail-late", datetime.now(timezone.utc) - timedelta(days=2), "buyer@example.com"
    )
    state = InboundSyncState(history_id="10")

    assert state.ingest(delayed) is True

