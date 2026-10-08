from __future__ import annotations

import pytest

from inventory_sales_engine.domain.enums import ReplyClass
from inventory_sales_engine.replies.detection import deterministic_reply_class


@pytest.mark.parametrize(
    "body",
    ["Unsubscribe", "Please remove me from your list.", "opt me out", "Stop emailing us"],
)
def test_unsubscribe_variations_are_detected_before_llm(body: str) -> None:
    assert deterministic_reply_class(body) is ReplyClass.UNSUBSCRIBE


@pytest.mark.parametrize("body", ["Not interested", "No thanks", "Please don't contact us again"])
def test_negative_variations_are_deterministic(body: str) -> None:
    assert deterministic_reply_class(body) is ReplyClass.NOT_INTERESTED


def test_ambiguous_message_is_left_for_structured_classification() -> None:
    assert deterministic_reply_class("Can you send more information?") is None

