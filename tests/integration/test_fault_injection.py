import unittest

from src.adapters.mock_llm import (
    ConnectionFailureError,
    FaultType,
    LLMTimeoutError,
    MockLLM,
    QuotaExceededError,
    UpstreamUnavailableError,
)
from src.fault_injection.controller import FaultInjectionController


class FaultInjectionTests(unittest.TestCase):
    def test_allowlisted_429_can_be_injected_and_cleared(self):
        dependency = MockLLM()
        controller = FaultInjectionController(dependency)
        controller.inject("mock-llm", FaultType.HTTP_429, count=3)
        with self.assertRaises(QuotaExceededError):
            dependency.generate(self._request())
        controller.clear("mock-llm")
        self.assertEqual(dependency.generate(self._request()).status, "ok")

    def test_non_mock_target_is_rejected(self):
        controller = FaultInjectionController(MockLLM())
        with self.assertRaises(PermissionError):
            controller.inject("production-llm", FaultType.HTTP_429)

    def test_count_is_bounded(self):
        controller = FaultInjectionController(MockLLM())
        with self.assertRaises(ValueError):
            controller.inject("mock-llm", FaultType.HTTP_429, count=11)

    def test_all_allowlisted_faults_are_reproducible(self):
        cases = [
            (FaultType.HTTP_429, QuotaExceededError),
            (FaultType.TIMEOUT, LLMTimeoutError),
            (FaultType.CONNECTION_FAILURE, ConnectionFailureError),
            (FaultType.HTTP_5XX, UpstreamUnavailableError),
        ]
        for fault, expected in cases:
            with self.subTest(fault=fault):
                dependency = MockLLM()
                controller = FaultInjectionController(dependency)
                controller.inject("mock-llm", fault, count=3)
                with self.assertRaises(expected):
                    dependency.generate(self._request())
                controller.clear("mock-llm")

    def test_repeated_injection_can_be_reset(self):
        dependency = MockLLM()
        controller = FaultInjectionController(dependency)
        controller.inject("mock-llm", FaultType.HTTP_5XX, count=3)
        self.assertEqual(controller.status()["remaining"], 3)
        controller.clear("mock-llm")
        self.assertEqual(controller.status()["fault"], "none")

    @staticmethod
    def _request():
        from src.domain.coaching import CoachingRequest

        return CoachingRequest("책", 10000, "읽고 싶다")


if __name__ == "__main__":
    unittest.main()
