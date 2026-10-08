from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    id: str
    source_url: str
    retrieved_at: datetime
    page_title: str | None
    content_hash: str
    excerpt: str

