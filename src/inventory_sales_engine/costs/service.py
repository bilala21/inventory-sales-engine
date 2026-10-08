from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import uuid4


class MonthlyBudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class CostAuthorization:
    id: str
    provider: str
    operation: str
    estimated_cost_usd: float
    on: date


class CostLedger:
    def __init__(self, *, monthly_budget_usd: float) -> None:
        self._budget = monthly_budget_usd
        self._reserved: dict[str, CostAuthorization] = {}
        self._actual: list[tuple[date, float]] = []
        self.paused = False

    @staticmethod
    def _same_month(first: date, second: date) -> bool:
        return (first.year, first.month) == (second.year, second.month)

    def preauthorize(
        self, provider: str, operation: str, estimated_cost_usd: float, *, on: date
    ) -> CostAuthorization:
        committed = self.monthly_cost(on)
        reserved = sum(
            item.estimated_cost_usd
            for item in self._reserved.values()
            if self._same_month(item.on, on)
        )
        if committed + reserved + estimated_cost_usd > self._budget:
            self.paused = True
            raise MonthlyBudgetExceeded("Provider call would exceed monthly API budget")
        authorization = CostAuthorization(
            str(uuid4()), provider, operation, estimated_cost_usd, on
        )
        self._reserved[authorization.id] = authorization
        return authorization

    def record(self, authorization: CostAuthorization, *, actual_cost_usd: float) -> None:
        existing = self._reserved.pop(authorization.id, None)
        if existing != authorization:
            raise ValueError("Cost was not preauthorized or was already recorded")
        self._actual.append((authorization.on, actual_cost_usd))
        if self.monthly_cost(authorization.on) > self._budget:
            self.paused = True

    def monthly_cost(self, on: date) -> float:
        return sum(cost for incurred, cost in self._actual if self._same_month(incurred, on))

    def cost_per(self, outcome_count: int, *, on: date) -> float | None:
        if outcome_count <= 0:
            return None
        return self.monthly_cost(on) / outcome_count

