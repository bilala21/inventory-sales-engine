from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from uuid import uuid4

from inventory_sales_engine.personalization.claims import ClaimRegistry


class DraftingError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class GroundedFact:
    text: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MessageDraft:
    id: str
    version: int
    subject: str
    body: str
    content_hash: str
    provenance: tuple[str, ...]


def _content_hash(subject: str, body: str) -> str:
    return sha256(f"{subject}\n{body}".encode()).hexdigest()


class DraftingService:
    def __init__(self, claims: ClaimRegistry) -> None:
        self._claims = claims

    def create_draft(
        self,
        *,
        contact_first_name: str,
        company_name: str,
        observation: GroundedFact,
        product_claim_id: str,
        cta: str,
    ) -> MessageDraft:
        if not observation.text.strip() or not observation.evidence_ids:
            raise DraftingError("Personalization facts require evidence")
        claim = self._claims.approved(product_claim_id)
        if claim is None:
            raise DraftingError("Product claim is not approved")
        subject = f"Inventory checking at {company_name}"
        body = (
            f"Hi {contact_first_name},\n\n"
            f"{observation.text.strip()}\n\n"
            "Quick question — does your team still spend time manually checking inventory or "
            "spreadsheets to decide what needs reordering?\n\n"
            f"I built a system that {claim.text.rstrip('.')} without forcing a replacement of the "
            "current spreadsheet or workflow.\n\n"
            f"{cta.strip()}"
        )
        provenance = tuple(
            [*(f"evidence:{evidence_id}" for evidence_id in observation.evidence_ids), f"product_claim:{claim.id}"]
        )
        return MessageDraft(
            id=str(uuid4()),
            version=1,
            subject=subject,
            body=body,
            content_hash=_content_hash(subject, body),
            provenance=provenance,
        )

    def edit(self, draft: MessageDraft, *, body: str) -> MessageDraft:
        return replace(
            draft,
            version=draft.version + 1,
            body=body,
            content_hash=_content_hash(draft.subject, body),
        )


class DraftApprovalStore:
    def __init__(self) -> None:
        self._approvals: set[tuple[str, str]] = set()

    def approve(self, draft: MessageDraft) -> None:
        self._approvals.add((draft.id, draft.content_hash))

    def is_approved(self, draft: MessageDraft) -> bool:
        return (draft.id, draft.content_hash) in self._approvals
