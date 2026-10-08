from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from inventory_sales_engine.research.evidence import EvidenceRecord
from inventory_sales_engine.research.service import CandidateObservation, validate_observations


def evidence(evidence_id: str = "evidence-1") -> EvidenceRecord:
    return EvidenceRecord(
        id=evidence_id,
        source_url="https://example.com/about",
        retrieved_at=datetime.now(timezone.utc),
        page_title="About",
        content_hash="a" * 64,
        excerpt="We distribute protective packaging products from our Chicago warehouse.",
    )


def test_supported_observation_keeps_evidence_provenance() -> None:
    accepted = validate_observations(
        [CandidateObservation("They distribute packaging from Chicago.", ("evidence-1",))],
        {"evidence-1": evidence()},
    )

    assert accepted[0].evidence_ids == ("evidence-1",)


def test_unsupported_observation_is_discarded() -> None:
    accepted = validate_observations(
        [CandidateObservation("They use spreadsheets.", ("missing",))],
        {"evidence-1": evidence()},
    )

    assert accepted == ()


def test_evidence_records_are_immutable() -> None:
    record = evidence()
    with pytest.raises(FrozenInstanceError):
        record.excerpt = "changed"  # type: ignore[misc]

