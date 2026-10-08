from __future__ import annotations

from inventory_sales_engine.safety.suppression import InMemorySuppressionStore, SuppressionService


def test_exact_and_normalized_email_suppression() -> None:
    service = SuppressionService(InMemorySuppressionStore())
    service.suppress_email(" Ops@Example.COM ", reason="UNSUBSCRIBE")

    assert service.is_suppressed(email="ops@example.com") is True
    assert service.is_suppressed(email="other@example.com") is False


def test_domain_suppression_covers_all_domain_contacts() -> None:
    service = SuppressionService(InMemorySuppressionStore())
    service.suppress_domain("https://www.example.com/about", reason="COMPLAINT")

    assert service.is_suppressed(email="buyer@example.com") is True


def test_company_suppression_is_global() -> None:
    service = SuppressionService(InMemorySuppressionStore())
    service.suppress_company("company-1", reason="NOT_INTERESTED")

    assert service.is_suppressed(email="buyer@elsewhere.com", company_id="company-1") is True


def test_unsubscribe_suppression_is_permanent() -> None:
    store = InMemorySuppressionStore()
    service = SuppressionService(store)
    entry = service.suppress_email("buyer@example.com", reason="UNSUBSCRIBE")

    assert entry.expires_at is None
    assert store.entries[entry.key].reason == "UNSUBSCRIBE"

