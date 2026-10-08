from __future__ import annotations

from dataclasses import dataclass

from inventory_sales_engine.domain.enums import MessageState
from inventory_sales_engine.domain.models import SendEligibilityDecision
from inventory_sales_engine.mail.service import MailSubmission, SendService
from inventory_sales_engine.providers.gmail import GmailSendResult, ProviderRejected


class AllowPolicy:
    def evaluate_and_reserve(self, command: object) -> SendEligibilityDecision:
        return SendEligibilityDecision(True, reservation_id="reservation-1")


class BlockPolicy:
    def evaluate_and_reserve(self, command: object) -> SendEligibilityDecision:
        return SendEligibilityDecision(False, ("suppressed",))


@dataclass
class FakeGmail:
    outcome: object
    calls: int = 0

    def send(self, *, raw_message: bytes, thread_id: str | None) -> GmailSendResult:
        self.calls += 1
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return self.outcome  # type: ignore[return-value]


def submission() -> MailSubmission:
    return MailSubmission(b"raw", "thread-1", "<stable@example.com>")


def test_success_is_sent_confirmed_not_delivered() -> None:
    gmail = FakeGmail(GmailSendResult("gmail-1", "thread-1"))

    result = SendService(AllowPolicy(), gmail).submit(object(), submission())

    assert result.state is MessageState.SENT_CONFIRMED
    assert result.gmail_message_id == "gmail-1"


def test_policy_block_never_calls_gmail() -> None:
    gmail = FakeGmail(GmailSendResult("gmail-1", "thread-1"))

    result = SendService(BlockPolicy(), gmail).submit(object(), submission())

    assert result.state is MessageState.CANCELLED
    assert result.block_reasons == ("suppressed",)
    assert gmail.calls == 0


def test_timeout_or_lost_response_enters_unknown_without_retry() -> None:
    gmail = FakeGmail(TimeoutError("lost response"))

    result = SendService(AllowPolicy(), gmail).submit(object(), submission())

    assert result.state is MessageState.UNKNOWN_SEND_STATE
    assert gmail.calls == 1


def test_provider_rejection_is_cancelled_not_ambiguous() -> None:
    gmail = FakeGmail(ProviderRejected("bad recipient"))

    result = SendService(AllowPolicy(), gmail).submit(object(), submission())

    assert result.state is MessageState.CANCELLED
    assert result.error_code == "PROVIDER_REJECTED"

