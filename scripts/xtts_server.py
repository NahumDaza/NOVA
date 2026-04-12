from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from TTS.api import TTS


os.environ["COQUI_TOS_AGREED"] = "1"

app = FastAPI(title="NOVA XTTS Server")

SPEAKER_WAV = "/Users/macuser/nova-audio/nova-reference.wav"
AUDIO_DIR = Path("/Users/macuser/nova-audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")


class TTSRequest(BaseModel):
    text: str
    language: str = "es"


def prepare_text_for_speech(text: str) -> str:
    cleaned = text.strip()

    # pronunciación personalizada
    replacements = {
        "Nahum Daza": "NaúmDaza",
        "Nahum": "Naúm",
        "NOVA": "Nóva",
        "Odoo": "Odú",
        "Climasync": "Clima Sync",
    }

    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    # quitar encabezados que en voz suenan raros
    prefixes = [
        "Claro, aquí tienes un borrador del correo:",
        "Claro, aquí tienes el correo:",
        "Aquí tienes un borrador del correo:",
    ]
    for prefix in prefixes:
        cleaned = cleaned.replace(prefix, "").strip()

    # quitar asunto del texto hablado
    cleaned = re.sub(r"^Asunto:\s.*?(?:\n|$)", "", cleaned, flags=re.IGNORECASE).strip()

    # reemplazar signos que XTTS verbaliza raro
    cleaned = cleaned.replace(":", ",")
    cleaned = cleaned.replace(";", ",")
    cleaned = cleaned.replace("\n", " ")

    # quitar dobles espacios
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


@app.post("/synthesize")
def synthesize(request: TTSRequest):
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=AUDIO_DIR).name

    spoken_text = prepare_text_for_speech(request.text)

    tts.tts_to_file(
        text=spoken_text,
        speaker_wav=SPEAKER_WAV,
        file_path=output_path,
        language=request.language,
        split_sentences=True,
    )

    # agregar pequeño silencio al final 
    import subprocess

    fixed_output = output_path.replace(".wav", "_fixed.wav")

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", output_path,
        "-af", "apad=pad_dur=0.2,afade=t=out:st=0:d=0.3",
        fixed_output
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return {"audio_path": fixed_output}