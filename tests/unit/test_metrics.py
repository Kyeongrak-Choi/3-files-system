import unittest

from src.domain.incident import Incident
from src.observability.metrics import aggregate_metrics, incident_metrics


class MetricsTests(unittest.TestCase):
    def test_incident_metrics_have_mttd_and_attempts(self):
        incident = Incident("coaching", "http_429", ["429"], attempt=2)
        values = incident_metrics(incident)
        self.assertEqual(values["attempts"], 2)
        self.assertGreaterEqual(values["mttd_seconds"], 0)

    def test_aggregate_metrics(self):
        recovered = Incident("coaching", "http_429", [], state="recovered", attempt=3)
        escalated = Incident("coaching", "unknown", [], state="escalated")
        values = aggregate_metrics([recovered, escalated])
        self.assertEqual(values["recovery_success_rate"], 0.5)
        self.assertEqual(values["escalation_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
