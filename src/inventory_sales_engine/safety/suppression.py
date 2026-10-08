from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from threading import RLock

from inventory_sales_engine.db.repositories import normalize_domain, normalize_email


@dataclass(frozen=True, slots=True)
class SuppressionRecord:
    key: str
    scope: str
    reason: str
    expires_at: datetime | None = None


class InMemorySuppressionStore:
    def __init__(self) -> None:
        self.entries: dict[str, SuppressionRecord] = {}
        self._lock = RLock()

    def put(self, entry: SuppressionRecord) -> SuppressionRecord:
        with self._lock:
            existing = self.entries.get(entry.key)
            if existing is not None and existing.expires_at is None:
                return existing
            self.entries[entry.key] = entry
            return entry

    def contains(self, key: str) -> bool:
        with self._lock:
            entry = self.entries.get(key)
            if entry is None:
                return False
            return entry.expires_at is None or entry.expires_at > datetime.now(entry.expires_at.tzinfo)


class SuppressionService:
    def __init__(self, store: InMemorySuppressionStore) -> None:
        self.store = store

    def suppress_email(self, email: str, *, reason: str) -> SuppressionRecord:
        return self.store.put(
            SuppressionRecord(key=f"email:{normalize_email(email)}", scope="EMAIL", reason=reason)
        )

    def suppress_domain(self, domain: str, *, reason: str) -> SuppressionRecord:
        return self.store.put(
            SuppressionRecord(key=f"domain:{normalize_domain(domain)}", scope="DOMAIN", reason=reason)
        )

    def suppress_company(self, company_id: str, *, reason: str) -> SuppressionRecord:
        return self.store.put(
            SuppressionRecord(key=f"company:{company_id}", scope="COMPANY", reason=reason)
        )

    def is_suppressed(self, *, email: str, company_id: str | None = None) -> bool:
        normalized = normalize_email(email)
        domain = normalized.rpartition("@")[2]
        keys = [f"email:{normalized}", f"domain:{normalize_domain(domain)}"]
        if company_id:
            keys.append(f"company:{company_id}")
        return any(self.store.contains(key) for key in keys)

