from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class HistoryGap(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class InboundEvent:
    provider_event_id: str
    gmail_message_id: str
    received_at: datetime
    from_email: str


class InboundSyncState:
    def __init__(
        self,
        *,
        history_id: str,
        watch_expires_at: datetime | None = None,
    ) -> None:
        self.history_id = history_id
        self.watch_expires_at = watch_expires_at
        self.messages: dict[str, InboundEvent] = {}
        self._history_gap = False

    def ingest(self, event: InboundEvent) -> bool:
        if event.provider_event_id in self.messages:
            return False
        self.messages[event.provider_event_id] = event
        return True

    def mark_history_gap(self, error: HistoryGap) -> None:
        del error
        self._history_gap = True

    def is_healthy(self, *, now: datetime) -> bool:
        watch_expired = self.watch_expires_at is not None and self.watch_expires_at <= now
        return not self._history_gap and not watch_expired

    def recover_with_all_mail_sweep(
        self, events: list[InboundEvent], *, new_history_id: str
    ) -> None:
        for event in events:
            self.ingest(event)
        self.history_id = new_history_id
        self._history_gap = False
        self.watch_expires_at = None


class BounceDisposition(StrEnum):
    HARD_BOUNCE = "HARD_BOUNCE"
    AMBIGUOUS_STOP = "AMBIGUOUS_STOP"
    NOT_BOUNCE = "NOT_BOUNCE"


@dataclass(frozen=True, slots=True)
class BounceResult:
    disposition: BounceDisposition
    recipient: str | None = None
    status: str | None = None


def parse_bounce(subject: str, body: str) -> BounceResult:
    action = re.search(r"(?im)^Action:\s*failed\s*$", body)
    status = re.search(r"(?im)^Status:\s*([245]\.\d+\.\d+)\s*$", body)
    recipient = re.search(r"(?im)^Final-Recipient:\s*rfc822;\s*([^\s]+)\s*$", body)
    if action and status and status.group(1).startswith("5."):
        return BounceResult(
            BounceDisposition.HARD_BOUNCE,
            recipient=recipient.group(1) if recipient else None,
            status=status.group(1),
        )
    bounce_like = any(
        phrase in subject.casefold()
        for phrase in ("undeliverable", "delivery status notification", "mail delivery failed")
    )
    if bounce_like:
        return BounceResult(BounceDisposition.AMBIGUOUS_STOP)
    return BounceResult(BounceDisposition.NOT_BOUNCE)
