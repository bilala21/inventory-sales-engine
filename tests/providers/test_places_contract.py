from __future__ import annotations

import pytest

from inventory_sales_engine.providers.places import (
    BudgetExceeded,
    CostBudget,
    PLACES_FIELD_MASK,
    build_text_search_request,
    durable_place_data,
)


def test_places_request_uses_exact_minimum_field_mask_and_us_region() -> None:
    request = build_text_search_request("packaging distributor Chicago", page_size=10)

    assert request.headers["X-Goog-FieldMask"] == PLACES_FIELD_MASK
    assert request.json == {
        "textQuery": "packaging distributor Chicago",
        "pageSize": 10,
        "regionCode": "US",
    }


@pytest.mark.parametrize("page_size", [0, 21])
def test_places_page_size_is_bounded(page_size: int) -> None:
    with pytest.raises(ValueError):
        build_text_search_request("packaging distributor Illinois", page_size=page_size)


def test_budget_is_reserved_before_provider_call() -> None:
    budget = CostBudget(monthly_limit_usd=0.05)
    budget.reserve(0.03)

    with pytest.raises(BudgetExceeded):
        budget.reserve(0.03)


def test_only_place_id_and_query_provenance_are_durable_google_data() -> None:
    stored = durable_place_data(
        {
            "id": "place-123",
            "displayName": {"text": "Example Packaging"},
            "formattedAddress": "Chicago, IL",
            "websiteUri": "https://example.com",
        },
        query="packaging distributor Chicago",
    )

    assert stored == {"google_place_id": "place-123", "discovery_query": "packaging distributor Chicago"}

