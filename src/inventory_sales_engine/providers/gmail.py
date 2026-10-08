from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Protocol

from googleapiclient.errors import HttpError


GMAIL_OAUTH_SCOPES = (
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
)


class ProviderRejected(RuntimeError):
    pass


class OAuthSecret:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        self._value = value

    def get_secret_value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return "OAuthSecret('**********')"

    def __str__(self) -> str:
        return "**********"


@dataclass(frozen=True, slots=True)
class GmailSendResult:
    message_id: str
    thread_id: str


@dataclass(frozen=True, slots=True)
class GmailLocatedMessage:
    message_id: str
    thread_id: str
    rfc_message_id: str


class GmailAdapter(Protocol):
    def send(self, *, raw_message: bytes, thread_id: str | None) -> GmailSendResult: ...


class GoogleGmailAdapter:
    def __init__(self, service: Any, *, user_id: str = "me") -> None:
        self._service = service
        self._user_id = user_id

    def send(self, *, raw_message: bytes, thread_id: str | None) -> GmailSendResult:
        body: dict[str, str] = {
            "raw": base64.urlsafe_b64encode(raw_message).decode("ascii").rstrip("=")
        }
        if thread_id:
            body["threadId"] = thread_id
        try:
            response = (
                self._service.users()
                .messages()
                .send(userId=self._user_id, body=body)
                .execute()
            )
        except HttpError as error:
            raise ProviderRejected(f"Gmail rejected submission with HTTP {error.resp.status}") from error
        message_id = response.get("id")
        returned_thread_id = response.get("threadId")
        if not message_id or not returned_thread_id:
            raise ConnectionError("Gmail response lacked required identifiers")
        return GmailSendResult(message_id, returned_thread_id)

