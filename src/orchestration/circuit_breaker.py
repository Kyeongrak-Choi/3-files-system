"""Circuit breaker with a fixed 30 second cooldown policy."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


class CircuitBreaker:
    def __init__(self, threshold: int = 3, cooldown_seconds: int = 30) -> None:
        self.threshold = threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures = 0
        self.opened_at: datetime | None = None

    @property
    def is_open(self) -> bool:
        return self.opened_at is not None

    def record_failure(self) -> bool:
        self.failures += 1
        if self.failures >= self.threshold:
            self.opened_at = datetime.now(timezone.utc)
        return self.is_open

    def can_probe(self) -> bool:
        if not self.opened_at:
            return True
        return datetime.now(timezone.utc) >= self.opened_at + timedelta(seconds=self.cooldown_seconds)

    def close(self, approved: bool, health_ok: bool) -> None:
        if not approved or not health_ok:
            raise PermissionError("circuit requires approval and healthy dependency before close")
        self.failures = 0
        self.opened_at = None

