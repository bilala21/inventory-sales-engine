from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256

from inventory_sales_engine.domain.enums import VerificationStatus


class ReviewPacketError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ReviewCandidate:
    company_id: str
    company_name: str
    qualified_at: datetime
    fit_score: int
    fit_reason: str
    personalization_fact: str
    evidence_ids: tuple[str, ...]
    contact_email: str
    contact_source: str
    verification_status: VerificationStatus
    draft_subject: str
    draft_body: str
    draft_provenance: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReviewPacket:
    candidates: tuple[ReviewCandidate, ...]
    content_hash: str


class ReviewPacketService:
    def __init__(self) -> None:
        self._current_hash: str | None = None
        self._approved_hash: str | None = None

    @property
    def checkpoint_complete(self) -> bool:
        return self._current_hash is not None and self._approved_hash == self._current_hash

    def build(self, candidates: list[ReviewCandidate]) -> ReviewPacket:
        if len(candidates) < 10:
            raise ReviewPacketError("Ten qualified companies are required for the checkpoint")
        selected = tuple(sorted(candidates, key=lambda item: item.qualified_at)[:10])
        for candidate in selected:
            if candidate.fit_score < 70 or not candidate.fit_reason.strip():
                raise ReviewPacketError("Candidate qualification is incomplete")
            if not candidate.personalization_fact.strip() or not candidate.evidence_ids:
                raise ReviewPacketError("Candidate evidence is incomplete")
            if not candidate.contact_source.strip() or not candidate.contact_email.strip():
                raise ReviewPacketError("Contact provenance is incomplete")
            if candidate.verification_status is not VerificationStatus.VALID:
                raise ReviewPacketError("Contact verification is not VALID")
            if not candidate.draft_body.strip() or not candidate.draft_provenance:
                raise ReviewPacketError("Draft provenance is incomplete")
        serializable = []
        for candidate in selected:
            data = asdict(candidate)
            data["qualified_at"] = candidate.qualified_at.isoformat()
            data["verification_status"] = candidate.verification_status.value
            serializable.append(data)
        digest = sha256(
            json.dumps(serializable, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        self._current_hash = digest
        self._approved_hash = None
        return ReviewPacket(selected, digest)

    def approve(self, content_hash: str) -> None:
        if content_hash != self._current_hash:
            raise ReviewPacketError("Approval hash does not match the current packet")
        self._approved_hash = content_hash

