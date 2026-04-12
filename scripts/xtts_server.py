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


def split_text(text: str, max_chars: int = 120) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return [text]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = sentence

    if current:
        chunks.append(current)

    return chunks


@app.post("/synthesize")
def synthesize(request: TTSRequest):
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=AUDIO_DIR).name

    text = request.text.replace("Nahum Daza", "Naúm Daza").replace("Nahum", "Naúm").replace("NOVA", "Nóva")
    text = text.replace(":", ".").replace(";", ".").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()

    chunks = split_text(text, max_chars=120)

    if len(chunks) == 1:
        tts.tts_to_file(
            text=chunks[0],
            speaker_wav=SPEAKER_WAV,
            file_path=output_path,
            language=request.language,
            split_sentences=True,
        )
        return {"audio_path": output_path}

    part_paths = []
    try:
        for i, chunk in enumerate(chunks):
            part_path = str(Path(output_path).with_name(f"{Path(output_path).stem}_part_{i}.wav"))
            tts.tts_to_file(
                text=chunk,
                speaker_wav=SPEAKER_WAV,
                file_path=part_path,
                language=request.language,
                split_sentences=True,
            )
            part_paths.append(part_path)

        concat_list = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
        try:
            for part in part_paths:
                concat_list.write(f"file '{part}'\n")
            concat_list.flush()
            concat_list.close()

            import subprocess
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_list.name,
                    "-c", "copy",
                    output_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        finally:
            try:
                os.unlink(concat_list.name)
            except FileNotFoundError:
                pass

        return {"audio_path": output_path}

    finally:
        for part in part_paths:
            if os.path.exists(part):
                try:
                    os.remove(part)
                except OSError:
                    pass