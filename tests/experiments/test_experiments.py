from __future__ import annotations

import pytest

from inventory_sales_engine.experiments.service import (
    ExperimentLocked,
    ExperimentService,
    UnsafeExperimentVariable,
)


def test_locked_experiment_assignment_is_immutable() -> None:
    service = ExperimentService()
    experiment = service.create(
        "packaging-chicago-a",
        {"niche": "packaging distributors", "geography": "Chicago, IL", "cta": "10-minute demo"},
    )
    service.assign(experiment.id, "company-1")

    with pytest.raises(ExperimentLocked):
        service.update(experiment.id, {"cta": "different CTA"})


@pytest.mark.parametrize(
    "unsafe_key",
    ["outreach_enabled", "daily_send_limit", "suppression_policy", "verification_policy"],
)
def test_safety_settings_cannot_be_experiment_variables(unsafe_key: str) -> None:
    service = ExperimentService()

    with pytest.raises(UnsafeExperimentVariable):
        service.create("unsafe", {unsafe_key: True})


def test_company_assignment_cannot_change_between_experiments() -> None:
    service = ExperimentService()
    first = service.create("first", {"cta": "demo"})
    second = service.create("second", {"cta": "pilot"})
    service.assign(first.id, "company-1")

    with pytest.raises(ExperimentLocked):
        service.assign(second.id, "company-1")
