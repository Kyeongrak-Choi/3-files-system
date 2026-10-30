"""Minimal orchestrator for normal, recoverable, and escalated requests."""

from __future__ import annotations

from collections.abc import Callable

from src.agents.diagnosis import DiagnosisAgent
from src.agents.monitor import MonitorAgent
from src.agents.notification import NotificationAgent
from src.agents.recovery import RecoveryAgent
from src.agents.verification import VerificationAgent
from src.domain.coaching import CoachingResponse
from src.domain.incident import Incident
from src.repositories.incident_repository import IncidentRepository
from src.orchestration.circuit_breaker import CircuitBreaker


class Orchestrator:
    def __init__(self, repository: IncidentRepository | None = None, recovery: RecoveryAgent | None = None) -> None:
        self.repository = repository or IncidentRepository()
        self.monitor = MonitorAgent()
        self.diagnosis = DiagnosisAgent()
        self.recovery = recovery or RecoveryAgent(sleeper=lambda _: None)
        self.verification = VerificationAgent()
        self.notification = NotificationAgent()
        self.circuit = CircuitBreaker()

    def execute(self, operation: Callable[[], CoachingResponse]) -> tuple[CoachingResponse | None, Incident | None]:
        try:
            response = operation()
            return response, None
        except Exception as error:
            incident = self.monitor.observe_error(error)
            self.repository.save(incident)
            incident = self.diagnosis.diagnose(incident)
            self.repository.save(incident)
            if incident.state == "escalated":
                incident.record_event("notification", payload=self.notification.build_escalation(incident))
                self.repository.save(incident)
                return None, incident
            response = self.recovery.retry(incident, operation)
            if response is None:
                self.circuit.record_failure()
                if self.circuit.is_open:
                    incident.transition("circuit_open", "retry limit reached")
                response = self.recovery.fallback(incident)
            verification = self.verification.verify(incident, response)
            if verification.passed:
                incident.transition("recovered", verification.reason)
            else:
                self.circuit.record_failure()
                incident.transition("escalated", verification.reason)
                incident.record_event("notification", payload=self.notification.build_escalation(incident))
            incident.recovered_at = incident.events[-1]["timestamp"] if verification.passed else None
            self.repository.save(incident)
            return response, incident

