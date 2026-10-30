"""Small JSON-backed incident repository for the local MVP."""

from __future__ import annotations

import json
from pathlib import Path

from src.domain.incident import Incident


class IncidentRepository:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self._items: dict[str, Incident] = {}
        if self.path and self.path.exists():
            for raw in json.loads(self.path.read_text(encoding="utf-8") or "[]"):
                incident = Incident.from_dict(raw)
                self._items[incident.incident_id] = incident

    def save(self, incident: Incident) -> Incident:
        self._items[incident.incident_id] = incident
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps([item.to_dict() for item in self._items.values()], ensure_ascii=False), encoding="utf-8")
        return incident

    def get(self, incident_id: str) -> Incident:
        return self._items[incident_id]

    def all(self) -> list[Incident]:
        return list(self._items.values())

