from __future__ import annotations

import pytest

from inventory_sales_engine.personalization.claims import ClaimRegistry, ProductClaim
from inventory_sales_engine.personalization.service import (
    DraftApprovalStore,
    DraftingError,
    DraftingService,
    GroundedFact,
)


def registry() -> ClaimRegistry:
    return ClaimRegistry(
        [
            ProductClaim(
                id="claim-monitor",
                text="monitors an existing inventory file and flags low-stock products",
                approved=True,
                capability_reference="existing-product:inventory-monitoring",
            )
        ]
    )


def test_draft_uses_only_evidence_fact_and_approved_product_claim() -> None:
    draft = DraftingService(registry()).create_draft(
        contact_first_name="Sara",
        company_name="Example Packaging",
        observation=GroundedFact(
            "Your company distributes protective packaging from its Chicago warehouse.",
            evidence_ids=("evidence-1",),
        ),
        product_claim_id="claim-monitor",
        cta="Would a 10-minute demo be worth it?",
    )

    assert "protective packaging from its Chicago warehouse" in draft.body
    assert "monitors an existing inventory file" in draft.body
    assert draft.provenance == ("evidence:evidence-1", "product_claim:claim-monitor")
    assert len(draft.content_hash) == 64


def test_fact_without_evidence_is_rejected() -> None:
    with pytest.raises(DraftingError, match="evidence"):
        DraftingService(registry()).create_draft(
            contact_first_name="Sara",
            company_name="Example Packaging",
            observation=GroundedFact("They use spreadsheets.", evidence_ids=()),
            product_claim_id="claim-monitor",
            cta="Open to a demo?",
        )


def test_unapproved_or_unknown_product_claim_is_rejected() -> None:
    claims = ClaimRegistry([ProductClaim("claim-fake", "saves 50%", False, "none")])

    with pytest.raises(DraftingError, match="approved"):
        DraftingService(claims).create_draft(
            contact_first_name="Sara",
            company_name="Example",
            observation=GroundedFact("Example sells packaging.", ("evidence-1",)),
            product_claim_id="claim-fake",
            cta="Open to a demo?",
        )


def test_edit_invalidates_exact_hash_approval() -> None:
    service = DraftingService(registry())
    draft = service.create_draft(
        contact_first_name="Sara",
        company_name="Example",
        observation=GroundedFact("Example distributes packaging.", ("evidence-1",)),
        product_claim_id="claim-monitor",
        cta="Open to a demo?",
    )
    approvals = DraftApprovalStore()
    approvals.approve(draft)
    edited = service.edit(draft, body=draft.body + "\nAnother sentence.")

    assert approvals.is_approved(draft) is True
    assert approvals.is_approved(edited) is False
