from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProductClaim:
    id: str
    text: str
    approved: bool
    capability_reference: str


class ClaimRegistry:
    def __init__(self, claims: list[ProductClaim]) -> None:
        self._claims = {claim.id: claim for claim in claims}

    def approved(self, claim_id: str) -> ProductClaim | None:
        claim = self._claims.get(claim_id)
        if claim is None or not claim.approved or not claim.capability_reference.strip():
            return None
        return claim

