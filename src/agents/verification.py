"""Independent verification of recovery results."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.coaching import CoachingResponse
from src.domain.incident import Incident


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    checks: dict[str, bool]
    reason: str


class VerificationAgent:
    def verify(self, incident: Incident, response: CoachingResponse | None, health_ok: bool = True, response_ms: float = 0.0) -> VerificationResult:
        checks = {
            "healthcheck": health_ok,
            "response_schema": False,
            "response_time": response_ms <= 5000.0,
        }
        if response is not None:
            try:
                response.validate()
                checks["response_schema"] = True
            except ValueError:
                checks["response_schema"] = False
        passed = all(checks.values())
        incident.record_event("verification_complete", agent="Verification", checks=checks, passed=passed)
        return VerificationResult(passed, checks, "all checks passed" if passed else "one or more checks failed")

