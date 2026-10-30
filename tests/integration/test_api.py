import unittest

from fastapi.testclient import TestClient

from src.api.app import app, state


class ApiTests(unittest.TestCase):
    def setUp(self):
        state.clear_fault()
        self.client = TestClient(app)

    def test_root_health_and_openapi_docs(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/health").json()["status"], "ok")
        self.assertEqual(self.client.get("/docs").status_code, 200)
        self.assertEqual(self.client.get("/redoc").status_code, 200)
        self.assertIn("/coach", self.client.get("/openapi.json").json()["paths"])

    def test_normal_coaching_endpoint(self):
        response = self.client.post("/coach", json={"item_name": "책", "price": 10000, "reason": "읽기"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_fault_endpoint_returns_degraded_coaching(self):
        self.assertEqual(self.client.post("/fault", json={"fault": "http_429", "count": 3}).status_code, 200)
        response = self.client.post("/coach", json={"item_name": "책", "price": 10000, "reason": "읽기"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "degraded")
        self.assertEqual(self.client.delete("/fault").status_code, 200)


if __name__ == "__main__":
    unittest.main()
