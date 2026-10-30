"""Application service for the normal coaching request."""

from src.adapters.mock_llm import MockLLM
from src.domain.coaching import CoachingRequest, CoachingResponse


class CoachingService:
    def __init__(self, llm: MockLLM | None = None, timeout_seconds: float = 5.0) -> None:
        self.llm = llm or MockLLM()
        self.timeout_seconds = timeout_seconds

    def coach(self, payload: dict) -> CoachingResponse:
        request = CoachingRequest.from_dict(payload)
        response = self.llm.generate(request, timeout_seconds=self.timeout_seconds)
        response.validate()
        return response

