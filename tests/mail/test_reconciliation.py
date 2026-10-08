from __future__ import annotations

from inventory_sales_engine.domain.enums import MessageState
from inventory_sales_engine.mail.reconciliation import reconcile_unknown_send
from inventory_sales_engine.providers.gmail import GmailLocatedMessage


def test_unknown_send_reconciles_by_stable_rfc_message_id() -> None:
    located = GmailLocatedMessage("gmail-1", "thread-1", "<stable@example.com>")

    result = reconcile_unknown_send("<stable@example.com>", located)

    assert result.state is MessageState.SENT_CONFIRMED


def test_absent_reconciliation_remains_unknown_and_never_assumes_failure() -> None:
    result = reconcile_unknown_send("<stable@example.com>", None)

    assert result.state is MessageState.UNKNOWN_SEND_STATE

