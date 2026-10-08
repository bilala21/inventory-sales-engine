from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4


class ExperimentLocked(ValueError):
    pass


class UnsafeExperimentVariable(ValueError):
    pass


UNSAFE_VARIABLES = frozenset(
    {
        "outreach_enabled",
        "daily_send_limit",
        "suppression_policy",
        "verification_policy",
        "emergency_stop",
        "approval_mode",
    }
)


@dataclass(frozen=True, slots=True)
class ExperimentRecord:
    id: str
    name: str
    configuration: Mapping[str, Any]


class ExperimentService:
    def __init__(self) -> None:
        self._experiments: dict[str, ExperimentRecord] = {}
        self._assignments: dict[str, str] = {}

    def create(self, name: str, configuration: dict[str, Any]) -> ExperimentRecord:
        unsafe = UNSAFE_VARIABLES.intersection(configuration)
        if unsafe:
            raise UnsafeExperimentVariable(", ".join(sorted(unsafe)))
        record = ExperimentRecord(str(uuid4()), name, MappingProxyType(dict(configuration)))
        self._experiments[record.id] = record
        return record

    def assign(self, experiment_id: str, company_id: str) -> None:
        if experiment_id not in self._experiments:
            raise KeyError(experiment_id)
        existing = self._assignments.get(company_id)
        if existing is not None and existing != experiment_id:
            raise ExperimentLocked(f"Company {company_id} is assigned to experiment {existing}")
        self._assignments[company_id] = experiment_id

    def update(self, experiment_id: str, changes: dict[str, Any]) -> ExperimentRecord:
        if experiment_id in self._assignments.values():
            raise ExperimentLocked("Assigned experiments cannot be modified")
        current = self._experiments[experiment_id]
        merged = dict(current.configuration)
        merged.update(changes)
        unsafe = UNSAFE_VARIABLES.intersection(merged)
        if unsafe:
            raise UnsafeExperimentVariable(", ".join(sorted(unsafe)))
        updated = ExperimentRecord(current.id, current.name, MappingProxyType(merged))
        self._experiments[experiment_id] = updated
        return updated
