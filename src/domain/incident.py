"""Shared incident model and safe state transitions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


STATES = {
    "detected",
    "diagnosed",
    "recovering",
    "verifying",
    "recovered",
    "escalated",
    "circuit_open",
}

ALLOWED_TRANSITIONS = {
    "detected": {"diagnosed", "escalated"},
    "diagnosed": {"recovering", "escalated"},
    "recovering": {"verifying", "diagnosed", "circuit_open", "escalated"},
    "verifying": {"recovered", "diagnosed", "circuit_open", "escalated"},
    "circuit_open": {"recovering", "escalated", "verifying"},
    "recovered": set(),
    "escalated": set(),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Incident:
    service: str
    failure_type: str
    evidence: list[str]
    incident_id: str = field(default_factory=lambda: f"INC-{uuid4().hex[:10].upper()}")
    trace_id: str = field(default_factory=lambda: f"TRC-{uuid4().hex[:10].upper()}")
    state: str = "detected"
    attempt: int = 0
    recommended_action: str | None = None
    requires_human_approval: bool = False
    injected_at: str = field(default_factory=utc_now)
    detected_at: str = field(default_factory=utc_now)
    recovery_started_at: str | None = None
    recovered_at: str | None = None
    events: list[dict[str, Any]] = field(default_factory=list)

    def transition(self, new_state: str, reason: str = "") -> None:
        if new_state not in STATES:
            raise ValueError(f"unknown incident state: {new_state}")
        if new_state not in ALLOWED_TRANSITIONS[self.state]:
            raise ValueError(f"invalid transition {self.state} -> {new_state}")
        self.state = new_state
        self.events.append({"timestamp": utc_now(), "event": "state_transition", "state": new_state, "reason": reason})

    def record_event(self, event: str, **data: Any) -> None:
        self.events.append({"timestamp": utc_now(), "event": event, **data})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Incident":
        return cls(**data)

