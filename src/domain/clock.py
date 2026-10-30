"""Clock boundary used by metrics and deterministic tests."""

from datetime import datetime, timezone


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def elapsed_seconds(start: str, end: str) -> float:
    first = datetime.fromisoformat(start)
    last = datetime.fromisoformat(end)
    return max(0.0, (last - first).total_seconds())

