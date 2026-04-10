from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    language: str = Field(default="auto")


class ChatResponse(BaseModel):
    intent: str
    response: str
    correction: str | None = None
    approval_required: bool = False


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        result = orchestrator.handle(message=payload.message, language=payload.language)
        return ChatResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc