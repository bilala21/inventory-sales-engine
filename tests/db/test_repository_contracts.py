from __future__ import annotations

from inventory_sales_engine.db.repositories import (
    normalize_company_name,
    normalize_domain,
    normalize_email,
)


def test_email_normalization_is_stable() -> None:
    assert normalize_email("  Ops@Example.COM ") == "ops@example.com"


def test_domain_normalization_removes_url_noise() -> None:
    assert normalize_domain("HTTPS://WWW.Example.COM/about/") == "example.com"


def test_company_name_normalization_collapses_punctuation_and_spacing() -> None:
    assert normalize_company_name("  Acme Packaging,  Inc. ") == "acme packaging inc"
