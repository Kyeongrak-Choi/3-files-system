"""Structured logging with sensitive field filtering."""

from __future__ import annotations

import json
from typing import Any


SENSITIVE_KEYS = {"password", "api_key", "token", "authorization", "session_cookie", "purchase_note"}


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


def event_json(**fields: Any) -> str:
    return json.dumps(sanitize(fields), ensure_ascii=False, sort_keys=True)

