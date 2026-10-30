"""Human approval representation for the local MVP."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ApprovalDecision:
    approved: bool
    approver_role: str = "project-operator"
    timeout_seconds: int = 300


def require_approval(decision: ApprovalDecision) -> None:
    if not decision.approved:
        raise PermissionError("human approval is required")

