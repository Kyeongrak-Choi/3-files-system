"""FastAPI HTTP boundary for the Auto Healing MVP."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.adapters.mock_llm import FaultType, MockLLM
from src.agents.recovery import RecoveryAgent
from src.fault_injection.controller import FaultInjectionController
from src.orchestration.orchestrator import Orchestrator


class CoachingPayload(BaseModel):
    item_name: str = Field(..., min_length=1, examples=["무선 이어폰"])
    price: int = Field(..., gt=0, examples=[129000])
    reason: str = Field(..., min_length=1, examples=["기존 제품이 고장 났다"])


class FaultPayload(BaseModel):
    fault: FaultType = Field(default=FaultType.NONE, description="허용된 모의 LLM 장애 유형")
    count: int | None = Field(default=None, ge=1, le=10, description="장애 주입 반복 상한")


@dataclass
class AppState:
    llm: MockLLM
    faults: FaultInjectionController
    orchestrator: Orchestrator

    @classmethod
    def create(cls) -> "AppState":
        llm = MockLLM()
        return cls(llm, FaultInjectionController(llm), Orchestrator(recovery=RecoveryAgent(sleeper=lambda _: None)))

    def coach(self, payload: CoachingPayload) -> tuple[int, dict[str, Any]]:
        response, incident = self.orchestrator.execute(lambda: self._coach(payload.model_dump()))
        if incident is not None and incident.state == "escalated":
            return status.HTTP_503_SERVICE_UNAVAILABLE, {"status": "escalated", "incident_id": incident.incident_id}
        return status.HTTP_200_OK, response.to_dict() if response else {"status": "error"}

    def _coach(self, payload: dict[str, Any]):
        from src.services.coaching_service import CoachingService

        return CoachingService(self.llm).coach(payload)

    def inject(self, payload: FaultPayload) -> dict[str, object]:
        self.faults.inject("mock-llm", payload.fault, payload.count)
        return self.faults.status()

    def clear_fault(self) -> dict[str, object]:
        self.faults.clear("mock-llm")
        return self.faults.status()


state = AppState.create()
app = FastAPI(
    title="지름막 소비 고민 코칭 Auto Healing API",
    description="LLM 의존 서비스 장애를 탐지·복구·검증하는 3일 MVP API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/", tags=["system"], summary="서비스 안내")
def root() -> dict[str, Any]:
    return {
        "service": "jireumak-auto-healing",
        "status": "ok",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {"health": "GET /health", "coach": "POST /coach", "inject_fault": "POST /fault", "clear_fault": "DELETE /fault"},
    }


@app.get("/health", tags=["system"], summary="서비스 헬스체크")
def health() -> dict[str, Any]:
    return {"status": "ok", "dependency": state.faults.status()}


@app.post("/coach", tags=["coaching"], summary="소비 고민 코칭 요청")
def coach(payload: CoachingPayload) -> dict[str, Any]:
    result_status, body = state.coach(payload)
    if result_status == status.HTTP_503_SERVICE_UNAVAILABLE:
        raise HTTPException(status_code=result_status, detail=body)
    return body


@app.post("/fault", tags=["testing"], summary="테스트 장애 주입")
def inject_fault(payload: FaultPayload) -> dict[str, object]:
    return state.inject(payload)


@app.delete("/fault", tags=["testing"], summary="테스트 장애 해제")
def clear_fault() -> dict[str, object]:
    return state.clear_fault()

