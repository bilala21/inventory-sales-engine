from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
from email.policy import SMTP
from email.utils import formataddr
from typing import Protocol

from inventory_sales_engine.domain.enums import MessageState
from inventory_sales_engine.domain.models import SendEligibilityDecision
from inventory_sales_engine.providers.gmail import GmailAdapter, ProviderRejected


@dataclass(frozen=True, slots=True)
class ComplianceIdentity:
    sender_name: str
    sender_email: str
    physical_postal_address: str
    unsubscribe_url: str


@dataclass(frozen=True, slots=True)
class MailSubmission:
    raw_message: bytes
    thread_id: str | None
    rfc_message_id: str


@dataclass(frozen=True, slots=True)
class SubmissionResult:
    state: MessageState
    gmail_message_id: str | None = None
    gmail_thread_id: str | None = None
    block_reasons: tuple[str, ...] = ()
    error_code: str | None = None


class EligibilityPolicy(Protocol):
    def evaluate_and_reserve(self, command: object) -> SendEligibilityDecision: ...


def build_mime_message(
    *,
    identity: ComplianceIdentity,
    recipient: str,
    subject: str,
    body: str,
    message_id: str,
    in_reply_to: str | None = None,
    references: tuple[str, ...] = (),
) -> bytes:
    if not identity.sender_name.strip() or not identity.sender_email.strip():
        raise ValueError("Accurate sender identity is required")
    if not identity.physical_postal_address.strip():
        raise ValueError("A physical postal address is required")
    if not identity.unsubscribe_url.startswith("https://"):
        raise ValueError("A secure unsubscribe URL is required")
    if not message_id.startswith("<") or not message_id.endswith(">"):
        raise ValueError("A stable RFC Message-ID is required")

    message = EmailMessage(policy=SMTP)
    message["From"] = formataddr((identity.sender_name, identity.sender_email))
    message["To"] = recipient
    message["Subject"] = subject
    message["Message-ID"] = message_id
    message["List-Unsubscribe"] = f"<{identity.unsubscribe_url}>"
    message["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    if in_reply_to:
        message["In-Reply-To"] = in_reply_to
    if references:
        message["References"] = " ".join(references)
    footer = (
        f"\n\n---\nCommercial outreach from {identity.sender_name}\n"
        f"{identity.physical_postal_address}\n"
        "If you do not want further emails, reply unsubscribe or use this link: "
        f"{identity.unsubscribe_url}"
    )
    message.set_content(body.rstrip() + footer)
    return message.as_bytes()


class SendService:
    def __init__(self, policy: EligibilityPolicy, gmail: GmailAdapter) -> None:
        self._policy = policy
        self._gmail = gmail

    def submit(self, command: object, submission: MailSubmission) -> SubmissionResult:
        eligibility = self._policy.evaluate_and_reserve(command)
        if not eligibility.allowed:
            return SubmissionResult(MessageState.CANCELLED, block_reasons=eligibility.reasons)
        try:
            sent = self._gmail.send(
                raw_message=submission.raw_message,
                thread_id=submission.thread_id,
            )
        except ProviderRejected:
            return SubmissionResult(MessageState.CANCELLED, error_code="PROVIDER_REJECTED")
        except (TimeoutError, ConnectionError, OSError):
            return SubmissionResult(MessageState.UNKNOWN_SEND_STATE, error_code="AMBIGUOUS_PROVIDER_RESULT")
        return SubmissionResult(
            MessageState.SENT_CONFIRMED,
            gmail_message_id=sent.message_id,
            gmail_thread_id=sent.thread_id,
        )
