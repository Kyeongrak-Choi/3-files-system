import tempfile
import unittest
from pathlib import Path

from src.domain.incident import Incident
from src.repositories.incident_repository import IncidentRepository


class IncidentTests(unittest.TestCase):
    def test_valid_state_transitions_are_recorded(self):
        incident = Incident("coaching", "http_429", ["status=429"])
        incident.transition("diagnosed", "status code")
        incident.transition("recovering", "retry")
        self.assertEqual(incident.state, "recovering")
        self.assertEqual(len(incident.events), 2)

    def test_invalid_state_transition_is_rejected(self):
        incident = Incident("coaching", "timeout", ["timeout"])
        with self.assertRaises(ValueError):
            incident.transition("recovered")

    def test_repository_persists_attempt_and_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "incidents.json"
            incident = Incident("coaching", "http_429", ["status=429"], attempt=2)
            IncidentRepository(path).save(incident)
            loaded = IncidentRepository(path).get(incident.incident_id)
            self.assertEqual(loaded.attempt, 2)
            self.assertEqual(loaded.failure_type, "http_429")


if __name__ == "__main__":
    unittest.main()
