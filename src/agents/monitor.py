"""Monitor role: turn observable failures into incidents."""

from __future__ import annotations

from src.adapters.mock_llm import MockLLMError
from src.domain.incident import Incident


class MonitorAgent:
    def observe_error(self, error: Exception, injected_at: str | None = None) -> Incident:
        failure_type = getattr(error, "failure_type", "unknown")
        incident = Incident(
            service="consumption-coaching",
            failure_type=failure_type,
            evidence=[f"{type(error).__name__}: {error}"],
        )
        if injected_at:
            incident.injected_at = injected_at
        incident.record_event("monitor_detected", agent="Monitor", failure_type=failure_type)
        return incident

    def observe_health(self, healthy: bool, response_ms: float = 0.0) -> Incident | None:
        if healthy:
            return None
        incident = Incident("consumption-coaching", "health_check_failed", [f"response_ms={response_ms}"])
        incident.record_event("monitor_detected", agent="Monitor", response_ms=response_ms)
        return incident

