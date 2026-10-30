"""Incident timing and aggregate metric calculations."""

from __future__ import annotations

from src.domain.clock import elapsed_seconds
from src.domain.incident import Incident


def incident_metrics(incident: Incident) -> dict[str, float | str | None]:
    detected = elapsed_seconds(incident.injected_at, incident.detected_at)
    recovered = elapsed_seconds(incident.injected_at, incident.recovered_at) if incident.recovered_at else None
    return {"incident_id": incident.incident_id, "mttd_seconds": detected, "mttr_seconds": recovered, "attempts": incident.attempt, "state": incident.state}


def aggregate_metrics(incidents: list[Incident]) -> dict[str, float]:
    total = len(incidents)
    successful = sum(item.state == "recovered" for item in incidents)
    escalated = sum(item.state == "escalated" for item in incidents)
    attempts = sum(item.attempt for item in incidents)
    return {
        "total_incidents": float(total),
        "recovery_success_rate": successful / total if total else 0.0,
        "escalation_rate": escalated / total if total else 0.0,
        "average_attempts": attempts / successful if successful else 0.0,
    }

