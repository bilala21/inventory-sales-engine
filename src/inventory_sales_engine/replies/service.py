from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from inventory_sales_engine.domain.enums import ReplyClass
from inventory_sales_engine.replies.classification import ReplyClassification, validated_classification
from inventory_sales_engine.safety.suppression import SuppressionService


@dataclass(frozen=True, slots=True)
class ReplyAction:
    reply_class: ReplyClass
    sequence_paused: bool = True
    manual_review: bool = False
    notify_operator: bool = False
    auto_send: bool = False
    suggested_response: str | None = None
    reschedule_date: date | None = None


class ReplyService:
    def __init__(self, suppression: SuppressionService) -> None:
        self._suppression = suppression

    def handle(
        self,
        *,
        email: str,
        company_id: str,
        classification: ReplyClassification,
    ) -> ReplyAction:
        checked = validated_classification(classification)
        reply_class = checked.reply_class
        if reply_class is ReplyClass.UNSUBSCRIBE:
            self._suppression.suppress_email(email, reason="UNSUBSCRIBE")
            self._suppression.suppress_company(company_id, reason="UNSUBSCRIBE")
            return ReplyAction(reply_class)
        if reply_class is ReplyClass.INTERESTED:
            return ReplyAction(reply_class, notify_operator=True)
        if reply_class is ReplyClass.QUESTION:
            return ReplyAction(
                reply_class,
                manual_review=True,
                suggested_response=checked.suggested_response,
            )
        if reply_class is ReplyClass.OUT_OF_OFFICE:
            return ReplyAction(
                reply_class,
                manual_review=checked.return_date is None,
                reschedule_date=checked.return_date,
            )
        if reply_class in {ReplyClass.REFERRAL, ReplyClass.UNCLEAR}:
            return ReplyAction(reply_class, manual_review=True)
        return ReplyAction(reply_class)

