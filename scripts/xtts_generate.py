from __future__ import annotations

import os
import re
import sys
import tempfile
import subprocess
from pathlib import Path

from TTS.api import TTS


SPEAKER_WAV = "/Users/macuser/nova-audio/nova-reference.wav"


def split_text(text: str, max_chars: int = 120) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) <= max_chars:
        return [text]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
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


def concat_wavs(parts: list[str], output_path: str) -> None:
    concat_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    try:
        for part in parts:
            concat_file.write(f"file '{part}'\n")
        concat_file.flush()
        concat_file.close()

        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file.name,
            "-c", "copy",
            output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    finally:
        try:
            os.unlink(concat_file.name)
        except FileNotFoundError:
            pass


def main() -> int:
    if len(sys.argv) < 3:
        print("Uso: python xtts_generate.py <texto> <output_path>")
        return 1

    text = sys.argv[1].strip()
    output_path = sys.argv[2]

    os.environ["COQUI_TOS_AGREED"] = "1"

    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    chunks = split_text(text, max_chars=120)
    temp_parts: list[str] = []

    try:
        for i, chunk in enumerate(chunks):
            part_path = str(Path(output_path).with_name(f"{Path(output_path).stem}_part_{i}.wav"))

            tts.tts_to_file(
                text=chunk,
                speaker_wav=SPEAKER_WAV,
                file_path=part_path,
                language="es",
                split_sentences=True,
            )

            temp_parts.append(part_path)

        if len(temp_parts) == 1:
            os.replace(temp_parts[0], output_path)
        else:
            concat_wavs(temp_parts, output_path)

        print(output_path)
        return 0

    finally:
        for part in temp_parts:
            if part != output_path and os.path.exists(part):
                try:
                    os.remove(part)
                except OSError:
                    pass


if __name__ == "__main__":
    raise SystemExit(main())