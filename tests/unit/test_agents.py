import unittest

from src.adapters.mock_llm import FaultType, MockLLM
from src.agents.diagnosis import DiagnosisAgent
from src.agents.monitor import MonitorAgent
from src.agents.recovery import RecoveryAgent
from src.agents.verification import VerificationAgent
from src.agents.notification import NotificationAgent
from src.approval.approval_service import ApprovalDecision, require_approval
from src.domain.coaching import CoachingRequest
from src.orchestration.circuit_breaker import CircuitBreaker


class AgentTests(unittest.TestCase):
    def test_monitor_and_diagnosis_classify_429(self):
        llm = MockLLM(FaultType.HTTP_429)
        with self.assertRaises(Exception) as raised:
            llm.generate(CoachingRequest("책", 1000, "읽기"))
        incident = MonitorAgent().observe_error(raised.exception)
        diagnosed = DiagnosisAgent().diagnose(incident)
        self.assertEqual(diagnosed.failure_type, "http_429")
        self.assertEqual(diagnosed.recommended_action, "retry_with_backoff")

    def test_recovery_is_bounded_and_fallback_is_valid(self):
        from src.domain.incident import Incident

        incident = Incident("coaching", "http_429", ["429"])
        incident.transition("diagnosed", "test diagnosis")
        recovery = RecoveryAgent(sleeper=lambda _: None)
        result = recovery.retry(incident, lambda: (_ for _ in ()).throw(RuntimeError("still down")))
        self.assertIsNone(result)
        self.assertEqual(incident.attempt, 3)
        fallback = recovery.fallback(incident)
        self.assertEqual(fallback.status, "degraded")

    def test_verification_rejects_unhealthy_response(self):
        from src.domain.incident import Incident

        incident = Incident("coaching", "http_429", ["429"])
        result = VerificationAgent().verify(incident, None, health_ok=False)
        self.assertFalse(result.passed)

    def test_circuit_opens_at_three_failures(self):
        breaker = CircuitBreaker()
        breaker.record_failure()
        breaker.record_failure()
        self.assertFalse(breaker.is_open)
        self.assertTrue(breaker.record_failure())
        self.assertTrue(breaker.is_open)

    def test_circuit_requires_health_and_human_approval_to_close(self):
        breaker = CircuitBreaker(cooldown_seconds=0)
        breaker.record_failure(); breaker.record_failure(); breaker.record_failure()
        with self.assertRaises(PermissionError):
            breaker.close(approved=False, health_ok=True)
        breaker.close(approved=True, health_ok=True)
        self.assertFalse(breaker.is_open)

    def test_notification_contains_traceable_non_sensitive_evidence(self):
        from src.domain.incident import Incident

        incident = Incident("coaching", "unknown", ["status=unknown"])
        payload = NotificationAgent().build_escalation(incident)
        self.assertEqual(payload["incident_id"], incident.incident_id)
        self.assertTrue(payload["requires_human_approval"])

    def test_approval_rejects_unapproved_action(self):
        with self.assertRaises(PermissionError):
            require_approval(ApprovalDecision(approved=False))


if __name__ == "__main__":
    unittest.main()
