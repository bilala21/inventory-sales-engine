from __future__ import annotations

from dataclasses import dataclass


PLACES_FIELD_MASK = ",".join(
    (
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.websiteUri",
        "places.nationalPhoneNumber",
        "places.primaryType",
    )
)


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class PlacesRequest:
    headers: dict[str, str]
    json: dict[str, str | int]


class CostBudget:
    def __init__(self, *, monthly_limit_usd: float) -> None:
        self.limit = monthly_limit_usd
        self.reserved = 0.0

    def reserve(self, estimated_cost_usd: float) -> None:
        if estimated_cost_usd < 0:
            raise ValueError("Estimated cost cannot be negative")
        if self.reserved + estimated_cost_usd > self.limit:
            raise BudgetExceeded("Provider call would exceed the monthly API budget")
        self.reserved += estimated_cost_usd


def build_text_search_request(query: str, *, page_size: int = 10) -> PlacesRequest:
    query = " ".join(query.split())
    if not query:
        raise ValueError("query is required")
    if not 1 <= page_size <= 20:
        raise ValueError("page_size must be between 1 and 20")
    return PlacesRequest(
        headers={"X-Goog-FieldMask": PLACES_FIELD_MASK},
        json={"textQuery": query, "pageSize": page_size, "regionCode": "US"},
    )


def durable_place_data(place: dict, *, query: str) -> dict[str, str]:
    place_id = place.get("id")
    if not isinstance(place_id, str) or not place_id:
        raise ValueError("Google Place ID is required")
    return {"google_place_id": place_id, "discovery_query": query}

