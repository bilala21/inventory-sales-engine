from __future__ import annotations

import re

from inventory_sales_engine.domain.enums import ReplyClass


UNSUBSCRIBE_PATTERNS = (
    r"\bunsubscribe\b",
    r"\bremove me\b",
    r"\bopt (?:me )?out\b",
    r"\bstop (?:emailing|contacting)\b",
)
NEGATIVE_PATTERNS = (
    r"\bnot interested\b",
    r"\bno thanks\b",
    r"\bdon['’]?t contact (?:me|us) again\b",
)


def deterministic_reply_class(body: str) -> ReplyClass | None:
    normalized = " ".join(body.casefold().split())
    if any(re.search(pattern, normalized) for pattern in UNSUBSCRIBE_PATTERNS):
        return ReplyClass.UNSUBSCRIBE
    if any(re.search(pattern, normalized) for pattern in NEGATIVE_PATTERNS):
        return ReplyClass.NOT_INTERESTED
    return None

