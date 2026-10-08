from __future__ import annotations

from fastapi.testclient import TestClient

from inventory_sales_engine.api import create_app
from inventory_sales_engine.config import Settings


def test_health_and_safety_status_expose_fail_closed_defaults() -> None:
    client = TestClient(create_app(Settings(_env_file=None)))

    health = client.get("/health")
    safety = client.get("/safety/status")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert safety.json() == {
        "approval_mode": "REVIEW",
        "outreach_enabled": False,
        "emergency_stop": True,
        "max_new_emails_per_day": 20,
        "max_total_emails_per_day": 40,
        "max_qualified_companies": 100,
    }


def test_validation_targets_endpoint_reports_business_outcomes() -> None:
    client = TestClient(create_app(Settings(_env_file=None)))

    response = client.get("/validation-targets")

    assert response.json()["paid_pilots"] == 1
    assert response.json()["meaningful_conversations"] == 5
