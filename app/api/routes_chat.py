from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.orchestrator import Orchestrator

router = APIRouter()
orchestrator = Orchestrator()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    language: str = Field(default="auto")
    conversation_id: str = Field(default="default")
    use_memory: bool = Field(default=True)


class ChatResponse(BaseModel):
    intent: str
    response: str
    correction: str | None = None
    approval_required: bool = False
    conversation_id: str


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        result = orchestrator.handle(
            message=payload.message,
            language=payload.language,
            conversation_id=payload.conversation_id,
            use_memory=payload.use_memory,
        )
        return ChatResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc