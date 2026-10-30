"""Fault injection controller for the isolated mock dependency."""

from __future__ import annotations

from dataclasses import dataclass

from src.adapters.mock_llm import FaultType, MockLLM
from src.fault_injection.policy import validate_fault, validate_target


@dataclass
class FaultInjectionController:
    dependency: MockLLM
    active: FaultType = FaultType.NONE
    remaining: int | None = None

    def inject(self, target: str, fault: FaultType, count: int | None = None) -> None:
        validate_target(target)
        validate_fault(fault)
        if count is not None and (count < 1 or count > 10):
            raise ValueError("count must be between 1 and 10")
        self.active = fault
        self.remaining = count
        self.dependency.fault = fault

    def clear(self, target: str) -> None:
        validate_target(target)
        self.active = FaultType.NONE
        self.remaining = None
        self.dependency.fault = FaultType.NONE

    def status(self) -> dict[str, object]:
        return {"target": "mock-llm", "fault": self.active.value, "remaining": self.remaining}

