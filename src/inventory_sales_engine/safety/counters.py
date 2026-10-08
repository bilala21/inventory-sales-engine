from __future__ import annotations

from threading import RLock


class DailyCounterStore:
    def __init__(self) -> None:
        self._counts: dict[tuple[str, str], tuple[int, int]] = {}
        self._lock = RLock()

    def reserve(
        self,
        mailbox_id: str,
        send_date: str,
        *,
        is_new: bool,
        max_new: int,
        max_total: int,
    ) -> bool:
        with self._lock:
            key = (mailbox_id, send_date)
            new_count, total_count = self._counts.get(key, (0, 0))
            next_new = new_count + int(is_new)
            next_total = total_count + 1
            if next_new > max_new or next_total > max_total:
                return False
            self._counts[key] = (next_new, next_total)
            return True

    def snapshot(self, mailbox_id: str, send_date: str) -> tuple[int, int]:
        with self._lock:
            return self._counts.get((mailbox_id, send_date), (0, 0))

