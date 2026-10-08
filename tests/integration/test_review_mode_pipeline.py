from __future__ import annotations

from dataclasses import replace

from inventory_sales_engine.domain.enums import VerificationStatus
from inventory_sales_engine.personalization.claims import ClaimRegistry, ProductClaim
from inventory_sales_engine.personalization.service import DraftingService, GroundedFact
from inventory_sales_engine.qualification.service import QualificationFacts, qualify
from inventory_sales_engine.safety.counters import DailyCounterStore
from inventory_sales_engine.safety.eligibility import SendEligibilityService
from tests.safety.test_send_eligibility import eligible_command


def test_discovery_to_reviewed_draft_performs_zero_external_sends() -> None:
    facts = QualificationFacts(True, True, True, True, True, True, True, 90)
    qualification = qualify(facts)
    claims = ClaimRegistry(
        [ProductClaim("monitor", "monitors inventory and flags low-stock products", True, "product")]
    )
    draft = DraftingService(claims).create_draft(
        contact_first_name="Sara",
        company_name="Example Packaging",
        observation=GroundedFact(
            "Example Packaging distributes protective packaging in Illinois.", ("evidence-1",)
        ),
        product_claim_id="monitor",
        cta="Would a 10-minute demo be worth it?",
    )
    decision = SendEligibilityService(DailyCounterStore()).evaluate_and_reserve(
        replace(
            eligible_command(),
            outreach_enabled=False,
            verification_status=VerificationStatus.VALID,
        )
    )

    assert qualification.qualified is True
    assert draft.provenance == ("evidence:evidence-1", "product_claim:monitor")
    assert decision.allowed is False
    assert decision.reasons == ("outreach_disabled",)
