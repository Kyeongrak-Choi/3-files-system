"""Notification payload creation; no external message is sent by the MVP."""

from src.domain.incident import Incident


class NotificationAgent:
    def build_escalation(self, incident: Incident) -> dict[str, object]:
        return {
            "incident_id": incident.incident_id,
            "trace_id": incident.trace_id,
            "failure_type": incident.failure_type,
            "state": incident.state,
            "attempt": incident.attempt,
            "requires_human_approval": True,
            "evidence": list(incident.evidence),
        }

