from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QualificationFacts:
    distributor_or_manufacturer: bool
    physical_product_inventory: bool
    recurring_supplier_model: bool
    relevant_niche: bool
    active_website: bool
    identifiable_decision_maker: bool
    clear_pain_hypothesis: bool
    evidence_confidence: int
    hard_exclusions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class QualificationDecision:
    fit_score: int
    qualified: bool
    score_reasons: tuple[str, ...]
    block_reasons: tuple[str, ...]


WEIGHTS = (
    ("distributor_or_manufacturer", 20),
    ("physical_product_inventory", 20),
    ("recurring_supplier_model", 15),
    ("relevant_niche", 15),
    ("active_website", 10),
    ("identifiable_decision_maker", 10),
    ("clear_pain_hypothesis", 10),
)


def qualify(
    facts: QualificationFacts, *, minimum_score: int = 70, minimum_confidence: int = 70
) -> QualificationDecision:
    scored = tuple((name, weight) for name, weight in WEIGHTS if getattr(facts, name))
    fit_score = sum(weight for _, weight in scored)
    score_reasons = tuple(f"{name}:+{weight}" for name, weight in scored)
    block_reasons = [f"hard_exclusion:{reason}" for reason in facts.hard_exclusions]
    if fit_score < minimum_score:
        block_reasons.append("fit_score_below_threshold")
    if facts.evidence_confidence < minimum_confidence:
        block_reasons.append("evidence_confidence_below_threshold")
    return QualificationDecision(
        fit_score=fit_score,
        qualified=not block_reasons,
        score_reasons=score_reasons,
        block_reasons=tuple(block_reasons),
    )
