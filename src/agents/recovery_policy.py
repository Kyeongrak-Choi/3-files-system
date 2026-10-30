"""Allowlisted recovery actions and fixed retry policy."""

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (1.0, 2.0, 4.0)
REQUEST_TIMEOUT_SECONDS = 5.0
WORKFLOW_TIMEOUT_SECONDS = 30.0

ALLOWED_ACTIONS = {
    "retry_with_backoff",
    "fallback_response",
    "restart_mock_dependency",
    "escalate",
}


def validate_action(action: str) -> None:
    if action not in ALLOWED_ACTIONS:
        raise PermissionError(f"recovery action is not allowlisted: {action}")

