import json
import unittest

from src.observability.logging import event_json


class LoggingTests(unittest.TestCase):
    def test_sensitive_fields_are_redacted(self):
        payload = json.loads(event_json(token="secret", purchase_note="private", incident_id="INC-1"))
        self.assertEqual(payload["token"], "[REDACTED]")
        self.assertEqual(payload["purchase_note"], "[REDACTED]")
        self.assertEqual(payload["incident_id"], "INC-1")


if __name__ == "__main__":
    unittest.main()
