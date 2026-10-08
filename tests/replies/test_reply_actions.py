from __future__ import annotations

from datetime import date

import pytest

from inventory_sales_engine.domain.enums import ReplyClass
from inventory_sales_engine.replies.classification import ReplyClassification
from inventory_sales_engine.replies.service import ReplyService
from inventory_sales_engine.safety.suppression import InMemorySuppressionStore, SuppressionService


def service() -> tuple[ReplyService, SuppressionService]:
    suppression = SuppressionService(InMemorySuppressionStore())
    return ReplyService(suppression), suppression


@pytest.mark.parametrize(
    "reply_class",
    [
        ReplyClass.INTERESTED,
        ReplyClass.QUESTION,
        ReplyClass.NOT_INTERESTED,
        ReplyClass.UNSUBSCRIBE,
        ReplyClass.REFERRAL,
        ReplyClass.OUT_OF_OFFICE,
        ReplyClass.UNCLEAR,
    ],
)
def test_every_reply_class_stops_or_pauses_sequence_first(reply_class: ReplyClass) -> None:
    reply_service, _ = service()

    action = reply_service.handle(
        email="buyer@example.com",
        company_id="company-1",
        classification=ReplyClassification(reply_class, 95),
    )

    assert action.sequence_paused is True


def test_unsubscribe_is_suppressed_synchronously() -> None:
    reply_service, suppression = service()
    reply_service.handle(
        email="buyer@example.com",
        company_id="company-1",
        classification=ReplyClassification(ReplyClass.UNSUBSCRIBE, 100, deterministic=True),
    )

    assert suppression.is_suppressed(email="buyer@example.com", company_id="company-1") is True


def test_low_confidence_model_classification_becomes_unclear() -> None:
    reply_service, _ = service()

    action = reply_service.handle(
        email="buyer@example.com",
        company_id="company-1",
        classification=ReplyClassification(ReplyClass.INTERESTED, 60),
    )

    assert action.reply_class is ReplyClass.UNCLEAR
    assert action.manual_review is True


def test_question_response_is_suggestion_only() -> None:
    reply_service, _ = service()
    action = reply_service.handle(
        email="buyer@example.com",
        company_id="company-1",
        classification=ReplyClassification(
            ReplyClass.QUESTION, 95, suggested_response="Suggested answer"
        ),
    )

    assert action.suggested_response == "Suggested answer"
    assert action.auto_send is False


def test_ooo_reschedules_only_with_confident_return_date() -> None:
    reply_service, _ = service()
    action = reply_service.handle(
        email="buyer@example.com",
        company_id="company-1",
        classification=ReplyClassification(
            ReplyClass.OUT_OF_OFFICE, 95, return_date=date(2026, 8, 24)
        ),
    )

    assert action.reschedule_date == date(2026, 8, 24)

