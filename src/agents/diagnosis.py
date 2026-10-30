"""Diagnosis role: deterministic failure classification and strategy selection."""

from __future__ import annotations

from src.domain.incident import Incident


STRATEGIES = {
    "http_429": ("retry_with_backoff", "fallback_response"),
    "timeout": ("retry_with_backoff", "fallback_response"),
    "connection_failure": ("retry_with_backoff", "restart_mock_dependency"),
    "http_5xx": ("retry_with_backoff", "restart_mock_dependency"),
    "repeated_failure": ("escalate",),
}


class DiagnosisAgent:
    def diagnose(self, incident: Incident) -> Incident:
        actions = STRATEGIES.get(incident.failure_type)
        if not actions:
            incident.recommended_action = "escalate"
            incident.requires_human_approval = True
            incident.transition("escalated", "unknown failure type")
            incident.record_event("diagnosis_complete", agent="Diagnosis", result="unknown", action="escalate")
            return incident
        incident.recommended_action = actions[0]
        incident.record_event("diagnosis_complete", agent="Diagnosis", result=incident.failure_type, action=actions[0], alternatives=list(actions[1:]))
        incident.transition("diagnosed", "allowlisted failure type")
        return incident

