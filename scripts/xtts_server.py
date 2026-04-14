from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from TTS.api import TTS


os.environ["COQUI_TOS_AGREED"] = "1"

app = FastAPI(title="NOVA XTTS Server")

SPEAKER_WAV = SPEAKER_WAV = "/Users/macuser/nova-audio/nova-reference-v4.wav"
AUDIO_DIR = Path("/Users/macuser/nova-audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Límite conservador para evitar el error de XTTS.
# No está en tokens exactos, pero funciona bien como guardrail práctico.
MAX_CHARS_PER_CHUNK = 280


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str = "es"


def prepare_text_for_speech(text: str) -> str:
    cleaned = text.strip()

    replacements = {
        "Nahum Daza": "Naúm Daza",
        "Nahum": "Naúm",
        "NOVA": "Terra",
        "Nóva": "Terra",
        "TERRA": "Terra",
        "Odoo": "Odú",
        "Climasync": "Clima Sainc",
    }

    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    prefixes = [
        "Claro, aquí tienes un borrador del correo:",
        "Claro, aquí tienes el correo:",
        "Aquí tienes un borrador del correo:",
    ]
    for prefix in prefixes:
        cleaned = cleaned.replace(prefix, "").strip()

    cleaned = re.sub(r"^Asunto:\s.*?(?:\n|$)", "", cleaned, flags=re.IGNORECASE).strip()

    cleaned = cleaned.replace(":", ",")
    cleaned = cleaned.replace(";", ",")
    cleaned = cleaned.replace("\n", " ")

    cleaned = re.sub(r"\[[^\]]+\]", "", cleaned)
    cleaned = cleaned.replace("Asunto", "")
    cleaned = cleaned.replace("Atentamente", "")
    cleaned = cleaned.replace("...", ".")
    cleaned = cleaned.replace("..", ".")
    cleaned = cleaned.replace("¿", "")
    cleaned = cleaned.replace("?", ".")
    cleaned = cleaned.replace("¡", "")
    cleaned = cleaned.replace("!", ".")
    cleaned = cleaned.replace("Hola, hola", "Hola")
    cleaned = cleaned.replace("TERRA", "Terra")
    cleaned = cleaned.replace("terra", "Terra")

    cleaned = cleaned.replace(" por un inconveniente personal.", " por un inconveniente personal")
    cleaned = cleaned.replace(" Gracias por su comprensión.", " Gracias por su comprensión")
    cleaned = cleaned.replace(" Le agradecería si me pudiera indicar", " Le agradecería que me indicara")
    cleaned = cleaned.replace(" así como", " y también")
    cleaned = cleaned.replace("Downloads", "Descargas")
    cleaned = cleaned.replace("Documents", "Documentos")
    cleaned = cleaned.replace("Desktop", "Escritorio")
    cleaned = cleaned.replace("Finder", "Finder")
    cleaned = cleaned.replace("Google Chrome", "Chrome")
    cleaned = cleaned.replace("Visual Studio Code", "VS Code")
    cleaned = cleaned.replace("Notes", "Notas")
    cleaned = cleaned.replace("Reminders", "Recordatorios")

    greeting_replacements = {
        "Hola, soy NOVA con mi nueva voz": "Soy Nóva con mi nueva voz",
        "Hola. soy NOVA con mi nueva voz": "Soy Nóva con mi nueva voz",
        "Hola. Soy NOVA con mi nueva voz": "Soy Nóva con mi nueva voz",
        "Hola, soy NOVA.": "Soy Nóva.",
        "Hola. Soy NOVA.": "Soy Nóva.",
        "Hola. soy NOVA.": "Soy Nóva.",
        "Hola, soy NOVA": "Soy Nóva",
        "Hola. Soy NOVA": "Soy Nóva",
    }
    for old, new in greeting_replacements.items():
        cleaned = cleaned.replace(old, new)

    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,")

    # Dejamos puntuación suave para pausas naturales
    cleaned = cleaned.replace(", ,", ",")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if cleaned.lower() in {"hola. soy nóva", "hola. soy nova", "hola soy nova", "hola, soy nova"}:
        cleaned = "Soy Nóva."

    return cleaned


def split_into_sentences(text: str) -> list[str]:
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> list[str]:
    text = prepare_text_for_speech(text)
    if not text:
        return []

    sentences = split_into_sentences(text)
    if not sentences:
        return [text[:max_chars]]

    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        # Si una oración sola es demasiado larga, la partimos duro
        if len(sentence) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""

            start = 0
            while start < len(sentence):
                piece = sentence[start:start + max_chars].strip()
                if piece:
                    chunks.append(piece)
                start += max_chars
            continue

        candidate = f"{current} {sentence}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            current = sentence

    if current:
        chunks.append(current.strip())

    return chunks


def synthesize_chunk(text: str, language: str) -> str:
    output_path = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav",
        dir=AUDIO_DIR,
    ).name

    tts.tts_to_file(
        text=text,
        speaker_wav=SPEAKER_WAV,
        file_path=output_path,
        language=language,
        split_sentences=True,
    )

    fixed_output = output_path.replace(".wav", "_fixed.wav")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            output_path,
            "-af",
            "apad=pad_dur=0.25,highpass=f=80,lowpass=f=8000",
            fixed_output,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    return fixed_output


def merge_wav_files(audio_paths: list[str]) -> str:
    if not audio_paths:
        raise ValueError("No audio files to merge.")

    if len(audio_paths) == 1:
        return audio_paths[0]

    concat_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".txt",
        dir=AUDIO_DIR,
        mode="w",
        encoding="utf-8",
    )

    try:
        for path in audio_paths:
            concat_file.write(f"file '{Path(path).as_posix()}'\n")
        concat_file.flush()
        concat_file.close()

        merged_output = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav",
            dir=AUDIO_DIR,
        ).name

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                concat_file.name,
                "-c",
                "copy",
                merged_output,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

        final_output = merged_output.replace(".wav", "_final.wav")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                merged_output,
                "-af",
                "highpass=f=80,lowpass=f=8000",
                final_output,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

        return final_output

    finally:
        try:
            Path(concat_file.name).unlink(missing_ok=True)
        except Exception:
            pass


@app.post("/synthesize")
def synthesize(request: TTSRequest):
    try:
        chunks = chunk_text(request.text)

        if not chunks:
            raise HTTPException(status_code=400, detail="Text is empty after cleaning.")

        audio_paths: list[str] = []
        for chunk in chunks:
            audio_paths.append(synthesize_chunk(chunk, request.language))

        final_audio_path = merge_wav_files(audio_paths)

        return {
            "audio_path": final_audio_path,
            "chunks_used": len(chunks),
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"XTTS synthesis failed: {exc}") from exc