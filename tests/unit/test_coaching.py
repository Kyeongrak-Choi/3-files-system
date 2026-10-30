import unittest

from src.adapters.mock_llm import MockLLM
from src.domain.coaching import CoachingRequest
from src.services.coaching_service import CoachingService


class CoachingContractTests(unittest.TestCase):
    def test_normal_request_returns_valid_coaching_response(self):
        response = CoachingService().coach(
            {"item_name": "무선 이어폰", "price": 129000, "reason": "기존 제품이 고장 났다"}
        )
        self.assertEqual(response.status, "ok")
        self.assertGreaterEqual(len(response.questions), 3)
        self.assertTrue(response.review)

    def test_invalid_input_is_rejected_before_dependency_call(self):
        service = CoachingService()
        with self.assertRaises(ValueError):
            service.coach({"item_name": "", "price": 1000, "reason": "테스트"})

    def test_mock_llm_is_deterministic_for_same_request(self):
        request = CoachingRequest.from_dict(
            {"item_name": "책", "price": 20000, "reason": "읽고 싶다"}
        )
        first = MockLLM().generate(request).to_dict()
        second = MockLLM().generate(request).to_dict()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
