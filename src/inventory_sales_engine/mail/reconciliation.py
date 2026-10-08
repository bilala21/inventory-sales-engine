from __future__ import annotations

from inventory_sales_engine.domain.enums import MessageState
from inventory_sales_engine.mail.service import SubmissionResult
from inventory_sales_engine.providers.gmail import GmailLocatedMessage


def reconcile_unknown_send(
    expected_rfc_message_id: str, located: GmailLocatedMessage | None
) -> SubmissionResult:
    if located is None or located.rfc_message_id != expected_rfc_message_id:
        return SubmissionResult(MessageState.UNKNOWN_SEND_STATE)
    return SubmissionResult(
        MessageState.SENT_CONFIRMED,
        gmail_message_id=located.message_id,
        gmail_thread_id=located.thread_id,
    )
