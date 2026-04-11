from fastapi import APIRouter
from pydantic import BaseModel
from app.services.tts_service import XTTSService

router = APIRouter()
tts_service = XTTSService()

class TTSRequest(BaseModel):
    text: str

@router.post("/speak")
def speak(request: TTSRequest):
    path = tts_service.synthesize(request.text)
    return {"audio_path": path}