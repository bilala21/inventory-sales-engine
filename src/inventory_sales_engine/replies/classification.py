from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from inventory_sales_engine.domain.enums import ReplyClass


@dataclass(frozen=True, slots=True)
class ReplyClassification:
    reply_class: ReplyClass
    confidence_score: int
    deterministic: bool = False
    suggested_response: str | None = None
    return_date: date | None = None


def validated_classification(
    classification: ReplyClassification, *, minimum_confidence: int = 80
) -> ReplyClassification:
    if classification.deterministic or classification.confidence_score >= minimum_confidence:
        return classification
    return ReplyClassification(ReplyClass.UNCLEAR, classification.confidence_score)

