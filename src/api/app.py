"""Framework-free HTTP application boundary for the local MVP."""

from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from src.adapters.mock_llm import FaultType, MockLLM
from src.agents.recovery import RecoveryAgent
from src.fault_injection.controller import FaultInjectionController
from src.orchestration.orchestrator import Orchestrator


@dataclass
class AppState:
    llm: MockLLM
    faults: FaultInjectionController
    orchestrator: Orchestrator

    @classmethod
    def create(cls) -> "AppState":
        llm = MockLLM()
        return cls(llm, FaultInjectionController(llm), Orchestrator(recovery=RecoveryAgent(sleeper=lambda _: None)))

    def coach(self, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        response, incident = self.orchestrator.execute(lambda: self._coach(payload))
        if incident is not None and incident.state == "escalated":
            return HTTPStatus.SERVICE_UNAVAILABLE, {"status": "escalated", "incident_id": incident.incident_id}
        return HTTPStatus.OK, response.to_dict() if response else {"status": "error"}

    def _coach(self, payload: dict[str, Any]):
        from src.services.coaching_service import CoachingService

        return CoachingService(self.llm).coach(payload)

    def inject(self, payload: dict[str, Any]) -> dict[str, Any]:
        fault = FaultType(payload.get("fault", FaultType.NONE.value))
        self.faults.inject("mock-llm", fault, payload.get("count"))
        return self.faults.status()

    def clear_fault(self) -> dict[str, Any]:
        self.faults.clear("mock-llm")
        return self.faults.status()


class RequestHandler(BaseHTTPRequestHandler):
    state = AppState.create()

    def _send(self, status: int, body: dict[str, Any]) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(HTTPStatus.OK, {"status": "ok", "dependency": self.state.faults.status()})
        else:
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = self._read_json()
            if self.path == "/coach":
                status, body = self.state.coach(payload)
            elif self.path == "/fault":
                status, body = HTTPStatus.OK, self.state.inject(payload)
            else:
                status, body = HTTPStatus.NOT_FOUND, {"error": "not_found"}
            self._send(status, body)
        except (ValueError, KeyError) as error:
            self._send(HTTPStatus.BAD_REQUEST, {"error": str(error)})

    def do_DELETE(self) -> None:  # noqa: N802
        if self.path == "/fault":
            self._send(HTTPStatus.OK, self.state.clear_fault())
        else:
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def log_message(self, *_args: object) -> None:
        return


def serve(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), RequestHandler)
    server.serve_forever()

