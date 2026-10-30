"""Deterministic LLM substitute used by the MVP and fault injection tests."""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum

from src.domain.coaching import CoachingRequest, CoachingResponse


class FaultType(str, Enum):
    NONE = "none"
    HTTP_429 = "http_429"
    TIMEOUT = "timeout"
    CONNECTION_FAILURE = "connection_failure"
    HTTP_5XX = "http_5xx"


class MockLLMError(RuntimeError):
    failure_type = "mock_llm_error"


class QuotaExceededError(MockLLMError):
    failure_type = "http_429"


class LLMTimeoutError(MockLLMError):
    failure_type = "timeout"


class ConnectionFailureError(MockLLMError):
    failure_type = "connection_failure"


class UpstreamUnavailableError(MockLLMError):
    failure_type = "http_5xx"


@dataclass
class MockLLM:
    fault: FaultType = FaultType.NONE
    delay_seconds: float = 0.0

    def generate(self, request: CoachingRequest, timeout_seconds: float = 5.0) -> CoachingResponse:
        if self.fault is FaultType.HTTP_429:
            raise QuotaExceededError("mock quota exceeded")
        if self.fault is FaultType.CONNECTION_FAILURE:
            raise ConnectionFailureError("mock dependency unavailable")
        if self.fault is FaultType.HTTP_5XX:
            raise UpstreamUnavailableError("mock upstream returned 5xx")
        if self.fault is FaultType.TIMEOUT:
            raise LLMTimeoutError("mock dependency timed out")
        if self.delay_seconds > timeout_seconds:
            raise LLMTimeoutError("mock dependency timed out")
        if self.delay_seconds:
            time.sleep(self.delay_seconds)
        return CoachingResponse(
            status="ok",
            questions=(
                f"{request.item_name}을 지금 꼭 사야 하는 이유는 무엇인가요?",
                "72시간 뒤에도 같은 필요를 느낄까요?",
                "현재 예산과 사용 계획에 무리가 없나요?",
            ),
            review=f"{request.item_name} 구매 이유와 {request.price:,}원 지출 계획을 72시간 동안 다시 점검해 보세요.",
        )

