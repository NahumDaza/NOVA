from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.stt_service import WhisperCppSTTService

router = APIRouter()
stt = WhisperCppSTTService()


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