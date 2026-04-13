from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.tts_service import XTTSService

router = APIRouter()
tts_service = XTTSService()


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1)
    intent: str | None = None


@router.post("/speak")
def speak(request: TTSRequest):
    try:
        audio_path = tts_service.synthesize(
            text=request.text,
            intent=request.intent,
        )
        return {"audio_path": audio_path}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {exc}") from exc