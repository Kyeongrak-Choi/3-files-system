import unittest

from src.adapters.mock_llm import FaultType, MockLLM
from src.domain.coaching import CoachingRequest
from src.orchestration.orchestrator import Orchestrator


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.request = CoachingRequest("책", 10000, "읽고 싶다")

    def test_normal_operation_has_no_incident(self):
        llm = MockLLM()
        response, incident = Orchestrator().execute(lambda: llm.generate(self.request))
        self.assertEqual(response.status, "ok")
        self.assertIsNone(incident)

    def test_recoverable_failure_returns_verified_fallback(self):
        llm = MockLLM(FaultType.HTTP_429)
        response, incident = Orchestrator().execute(lambda: llm.generate(self.request))
        self.assertEqual(response.status, "degraded")
        self.assertEqual(incident.state, "recovered")
        self.assertEqual(incident.attempt, 3)

    def test_unknown_failure_escalates_without_recovery(self):
        class UnknownError(RuntimeError):
            failure_type = "unknown"

        response, incident = Orchestrator().execute(lambda: (_ for _ in ()).throw(UnknownError("unknown")))
        self.assertIsNone(response)
        self.assertEqual(incident.state, "escalated")
        self.assertEqual(incident.attempt, 0)


if __name__ == "__main__":
    unittest.main()
