"""Domain contracts for the consumption coaching flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CoachingRequest:
    item_name: str
    price: int
    reason: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CoachingRequest":
        if not isinstance(payload, dict):
            raise ValueError("request payload must be an object")
        item_name = payload.get("item_name")
        reason = payload.get("reason")
        price = payload.get("price")
        if not isinstance(item_name, str) or not item_name.strip():
            raise ValueError("item_name is required")
        if isinstance(price, bool) or not isinstance(price, (int, float)) or price <= 0:
            raise ValueError("price must be a positive number")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason is required")
        return cls(item_name=item_name.strip(), price=int(price), reason=reason.strip())


@dataclass(frozen=True)
class CoachingResponse:
    status: str
    questions: tuple[str, ...]
    review: str
    retryable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "questions": list(self.questions),
            "review": self.review,
            "retryable": self.retryable,
        }

    def validate(self) -> None:
        if self.status not in {"ok", "degraded"}:
            raise ValueError("invalid coaching status")
        if not isinstance(self.questions, tuple) or not all(self.questions):
            raise ValueError("questions must contain non-empty strings")
        if not self.review:
            raise ValueError("review is required")

