from __future__ import annotations

from dataclasses import dataclass

from inventory_sales_engine.research.evidence import EvidenceRecord


@dataclass(frozen=True, slots=True)
class CandidateObservation:
    text: str
    evidence_ids: tuple[str, ...]


def validate_observations(
    candidates: list[CandidateObservation], evidence: dict[str, EvidenceRecord]
) -> tuple[CandidateObservation, ...]:
    return tuple(
        candidate
        for candidate in candidates
        if candidate.text.strip()
        and candidate.evidence_ids
        and all(evidence_id in evidence for evidence_id in candidate.evidence_ids)
    )

