from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
import subprocess

from app.core.orchestrator import Orchestrator
from app.services.stt_service import WhisperCppSTTService
from app.services.tts_service import XTTSService


router = APIRouter()
stt = WhisperCppSTTService()
orchestrator = Orchestrator()



class VoiceRespondRequest(BaseModel):
    message: str = Field(..., min_length=1)
    language: str = Field(default="es")
    conversation_id: str = Field(default="default")
    use_memory: bool = Field(default=True)


@router.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(...),
    language: str = "es",
):
    try:
        audio_bytes = await file.read()

        suffix = ".wav"
        if file.filename and "." in file.filename:
            suffix = "." + file.filename.split(".")[-1].lower()

        temp_path = stt.save_temp_audio(audio_bytes, suffix=suffix)
        transcript = stt.transcribe_file(temp_path, language=language)

        return {"transcript": transcript}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/respond")
def respond_to_voice(payload: VoiceRespondRequest):
    try:
        result = orchestrator.handle(
            message=payload.message,
            language=payload.language,
            conversation_id=payload.conversation_id,
            use_memory=payload.use_memory,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/respond-from-audio")
async def respond_from_audio(
    file: UploadFile = File(...),
    language: str = "es",
    conversation_id: str = "default",
    use_memory: bool = True,
):
    try:
        audio_bytes = await file.read()

        suffix = ".wav"
        if file.filename and "." in file.filename:
            suffix = "." + file.filename.split(".")[-1].lower()

        temp_path = stt.save_temp_audio(audio_bytes, suffix=suffix)
        transcript = stt.transcribe_file(temp_path, language=language)

        result = orchestrator.handle(
            message=transcript,
            language=language,
            conversation_id=conversation_id,
            use_memory=use_memory,
        )

        return {
            "transcript": transcript,
            "intent": result["intent"],
            "response": result["response"],
            "correction": result["correction"],
            "approval_required": result["approval_required"],
            "conversation_id": result["conversation_id"],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    


tts = XTTSService()


@router.post("/respond-with-audio")
async def respond_with_audio(
    file: UploadFile = File(...),
    language: str = "es",
    conversation_id: str = "default",
    use_memory: bool = True,
):
    try:
        audio_bytes = await file.read()

        suffix = ".wav"
        if file.filename and "." in file.filename:
            suffix = "." + file.filename.split(".")[-1].lower()

        temp_path = stt.save_temp_audio(audio_bytes, suffix=suffix)
        transcript = stt.transcribe_file(temp_path, language=language)

        result = orchestrator.handle(
            message=transcript,
            language=language,
            conversation_id=conversation_id,
            use_memory=use_memory,
        )

        audio_path = tts.synthesize(result["response"])
        subprocess.Popen(["afplay", audio_path])

        return {
            "transcript": transcript,
            "intent": result["intent"],
            "response": result["response"],
            "correction": result["correction"],
            "approval_required": result["approval_required"],
            "conversation_id": result["conversation_id"],
            "audio_path": audio_path,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc