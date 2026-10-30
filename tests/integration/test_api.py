import json
import threading
import unittest
from http.client import HTTPConnection

from src.api.app import RequestHandler
from http.server import ThreadingHTTPServer


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), RequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def request(self, method, path, payload=None):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=2)
        body = json.dumps(payload).encode() if payload is not None else None
        connection.request(method, path, body, {"Content-Type": "application/json"} if body else {})
        response = connection.getresponse()
        data = json.loads(response.read())
        connection.close()
        return response.status, data

    def test_health_and_normal_coaching_endpoint(self):
        status, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")
        status, body = self.request("POST", "/coach", {"item_name": "책", "price": 10000, "reason": "읽기"})
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_fault_endpoint_returns_degraded_coaching(self):
        status, _ = self.request("POST", "/fault", {"fault": "http_429", "count": 3})
        self.assertEqual(status, 200)
        status, body = self.request("POST", "/coach", {"item_name": "책", "price": 10000, "reason": "읽기"})
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "degraded")
        status, _ = self.request("DELETE", "/fault")
        self.assertEqual(status, 200)


if __name__ == "__main__":
    unittest.main()
