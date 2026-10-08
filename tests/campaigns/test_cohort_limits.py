from __future__ import annotations

import pytest

from inventory_sales_engine.campaigns.service import CohortLimitReached, QualificationCohort


def test_first_validation_cohort_is_hard_capped_at_100() -> None:
    cohort = QualificationCohort(max_companies=100)
    for index in range(100):
        cohort.add(f"company-{index}")

    with pytest.raises(CohortLimitReached):
        cohort.add("company-100")


def test_duplicate_company_does_not_consume_cohort_capacity() -> None:
    cohort = QualificationCohort(max_companies=100)

    assert cohort.add("company-1") is True
    assert cohort.add("company-1") is False
    assert cohort.count == 1

