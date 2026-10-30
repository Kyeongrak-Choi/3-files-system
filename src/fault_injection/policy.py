"""Allowlisted, test-only fault injection policy."""

from src.adapters.mock_llm import FaultType


ALLOWED_FAULTS = {
    FaultType.NONE,
    FaultType.HTTP_429,
    FaultType.TIMEOUT,
    FaultType.CONNECTION_FAILURE,
    FaultType.HTTP_5XX,
}


def validate_target(target: str) -> None:
    if target != "mock-llm":
        raise PermissionError("fault injection target must be mock-llm")


def validate_fault(fault: FaultType) -> None:
    if fault not in ALLOWED_FAULTS:
        raise ValueError(f"fault type is not allowlisted: {fault}")

