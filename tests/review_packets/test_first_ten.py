from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from inventory_sales_engine.domain.enums import VerificationStatus
from inventory_sales_engine.review_packets.service import (
    ReviewCandidate,
    ReviewPacketError,
    ReviewPacketService,
)


def candidate(index: int, **changes: object) -> ReviewCandidate:
    values = {
        "company_id": f"company-{index}",
        "company_name": f"Packaging Company {index}",
        "qualified_at": datetime(2026, 8, 18, tzinfo=timezone.utc) + timedelta(minutes=index),
        "fit_score": 80,
        "fit_reason": "Packaging distributor with physical inventory evidence.",
        "personalization_fact": "Distributes protective packaging in Illinois.",
        "evidence_ids": (f"evidence-{index}",),
        "contact_email": f"ops{index}@example{index}.com",
        "contact_source": "PUBLIC_WEBSITE",
        "verification_status": VerificationStatus.VALID,
        "draft_subject": "Inventory checking",
        "draft_body": "Evidence-grounded body",
        "draft_provenance": (f"evidence:evidence-{index}", "product_claim:monitor"),
    }
    values.update(changes)
    return ReviewCandidate(**values)  # type: ignore[arg-type]


def test_first_ten_packet_contains_exactly_earliest_ten_qualified_leads() -> None:
    service = ReviewPacketService()
    packet = service.build([candidate(index) for index in reversed(range(12))])

    assert len(packet.candidates) == 10
    assert [item.company_id for item in packet.candidates] == [f"company-{i}" for i in range(10)]
    assert service.checkpoint_complete is False


@pytest.mark.parametrize(
    "changes",
    [
        {"evidence_ids": ()},
        {"contact_source": ""},
        {"verification_status": VerificationStatus.UNKNOWN},
        {"draft_provenance": ()},
    ],
)
def test_incomplete_candidate_blocks_packet(changes: dict) -> None:
    candidates = [candidate(index) for index in range(10)]
    candidates[0] = candidate(0, **changes)

    with pytest.raises(ReviewPacketError):
        ReviewPacketService().build(candidates)


def test_operator_approval_is_bound_to_exact_packet_hash() -> None:
    service = ReviewPacketService()
    packet = service.build([candidate(index) for index in range(10)])
    service.approve(packet.content_hash)

    assert service.checkpoint_complete is True

