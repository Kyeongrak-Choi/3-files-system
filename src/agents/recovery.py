"""Recovery role with bounded retry and safe fallback."""

from __future__ import annotations

import time
from collections.abc import Callable

from src.agents.recovery_policy import BACKOFF_SECONDS, MAX_ATTEMPTS, validate_action
from src.domain.coaching import CoachingResponse
from src.domain.incident import Incident


class RecoveryAgent:
    def __init__(self, sleeper: Callable[[float], None] | None = None) -> None:
        self.sleeper = sleeper or time.sleep

    def retry(self, incident: Incident, operation: Callable[[], CoachingResponse]) -> CoachingResponse | None:
        validate_action("retry_with_backoff")
        incident.transition("recovering", "bounded retry started")
        for index in range(MAX_ATTEMPTS):
            incident.attempt += 1
            incident.record_event("recovery_attempt", agent="Recovery", attempt=incident.attempt)
            try:
                response = operation()
                incident.transition("verifying", "operation returned")
                return response
            except Exception as error:  # the caller records the final failure, not the raw value
                incident.record_event("recovery_failure", attempt=incident.attempt, error_type=type(error).__name__)
                if index < MAX_ATTEMPTS - 1:
                    self.sleeper(BACKOFF_SECONDS[index])
        return None

    def fallback(self, incident: Incident) -> CoachingResponse:
        validate_action("fallback_response")
        incident.record_event("fallback_response", agent="Recovery")
        incident.transition("verifying", "using predefined fallback")
        return CoachingResponse(
            status="degraded",
            questions=("지금 이 구매가 꼭 필요한지 72시간 뒤에도 다시 확인해 보세요.",),
            review="코칭 서비스가 일시적으로 지연되고 있습니다. 구매를 서두르지 말고 잠시 후 다시 시도해 주세요.",
            retryable=True,
        )

