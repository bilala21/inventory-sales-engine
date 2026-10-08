from __future__ import annotations

import pytest

from inventory_sales_engine.qualification.service import QualificationFacts, qualify


def strong_facts(**changes: object) -> QualificationFacts:
    values = {
        "distributor_or_manufacturer": True,
        "physical_product_inventory": True,
        "recurring_supplier_model": True,
        "relevant_niche": True,
        "active_website": True,
        "identifiable_decision_maker": True,
        "clear_pain_hypothesis": True,
        "evidence_confidence": 90,
        "hard_exclusions": (),
    }
    values.update(changes)
    return QualificationFacts(**values)  # type: ignore[arg-type]


def test_strong_packaging_distributor_qualifies_deterministically() -> None:
    decision = qualify(strong_facts(), minimum_score=70, minimum_confidence=70)

    assert decision.fit_score == 100
    assert decision.qualified is True


@pytest.mark.parametrize("exclusion", ["NON_US", "NO_PHYSICAL_INVENTORY", "HUGE_ENTERPRISE"])
def test_hard_exclusion_overrides_perfect_score(exclusion: str) -> None:
    decision = qualify(strong_facts(hard_exclusions=(exclusion,)))

    assert decision.fit_score == 100
    assert decision.qualified is False
    assert decision.block_reasons == (f"hard_exclusion:{exclusion}",)


def test_low_confidence_blocks_even_when_score_is_high() -> None:
    decision = qualify(strong_facts(evidence_confidence=69), minimum_confidence=70)

    assert decision.qualified is False
    assert "evidence_confidence_below_threshold" in decision.block_reasons


def test_score_below_threshold_blocks() -> None:
    facts = strong_facts(
        recurring_supplier_model=False,
        relevant_niche=False,
        identifiable_decision_maker=False,
    )
    decision = qualify(facts, minimum_score=70)

    assert decision.fit_score == 60
    assert decision.qualified is False
    assert "fit_score_below_threshold" in decision.block_reasons
