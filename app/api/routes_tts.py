from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.tts_service import XTTSService

router = APIRouter()
tts_service = XTTSService()


class TTSRequest(BaseModel):
    text: str


@router.post("/speak")
def speak(request: TTSRequest):
    try:
        path = tts_service.synthesize(request.text)
        return {"audio_path": path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc