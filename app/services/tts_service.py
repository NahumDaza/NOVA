from __future__ import annotations

import contextlib
import re
import uuid
import wave
from pathlib import Path
from typing import List

import httpx


class XTTSService:
    def __init__(self) -> None:
        self.base_url = "http://127.0.0.1:8010"
        self.max_chars_per_chunk = 320
        self.output_dir = Path("data/tts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _clean_text(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _split_into_sentences(self, text: str) -> List[str]:
        text = self._clean_text(text)
        if not text:
            return []
        parts = re.split(r"(?<=[.!?])\s+", text)
        return [p.strip() for p in parts if p.strip()]

    def _chunk_text(self, text: str) -> List[str]:
        sentences = self._split_into_sentences(text)
        if not sentences:
            return []

        chunks: List[str] = []
        current = ""

        for sentence in sentences:
            if len(sentence) > self.max_chars_per_chunk:
                if current:
                    chunks.append(current.strip())
                    current = ""

                start = 0
                while start < len(sentence):
                    piece = sentence[start:start + self.max_chars_per_chunk].strip()
                    if piece:
                        chunks.append(piece)
                    start += self.max_chars_per_chunk
                continue

            candidate = f"{current} {sentence}".strip()
            if len(candidate) <= self.max_chars_per_chunk:
                current = candidate
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence

        if current:
            chunks.append(current.strip())

        return chunks

    def _synthesize_chunk(self, text: str) -> str:
        response = httpx.post(
            f"{self.base_url}/synthesize",
            json={
                "text": text,
                "language": "es",
            },
            timeout=300.0,
        )
        response.raise_for_status()
        data = response.json()

        audio_path = data.get("audio_path")
        if not audio_path:
            raise ValueError("XTTS response did not include 'audio_path'.")

        return audio_path

    def _validate_wav_compatibility(self, wav_paths: List[Path]) -> tuple[int, int, int, int]:
        if not wav_paths:
            raise ValueError("No WAV files provided for merge.")

        with contextlib.closing(wave.open(str(wav_paths[0]), "rb")) as first:
            params = (
                first.getnchannels(),
                first.getsampwidth(),
                first.getframerate(),
                first.getcomptype(),
            )

        for path in wav_paths[1:]:
            with contextlib.closing(wave.open(str(path), "rb")) as wf:
                current = (
                    wf.getnchannels(),
                    wf.getsampwidth(),
                    wf.getframerate(),
                    wf.getcomptype(),
                )
                if current != params:
                    raise ValueError(
                        f"WAV files are not compatible for merge. "
                        f"Expected {params}, got {current} for {path}."
                    )

        return params

    def _merge_wav_files(self, wav_paths: List[str]) -> str:
        path_objs = [Path(p) for p in wav_paths]

        for path in path_objs:
            if path.suffix.lower() != ".wav":
                raise ValueError(
                    f"Expected WAV files for merge, but got: {path.name}"
                )
            if not path.exists():
                raise FileNotFoundError(f"Chunk audio file not found: {path}")

        nchannels, sampwidth, framerate, comptype = self._validate_wav_compatibility(path_objs)

        output_path = self.output_dir / f"tts_merged_{uuid.uuid4().hex}.wav"

        with contextlib.closing(wave.open(str(output_path), "wb")) as out_wav:
            out_wav.setnchannels(nchannels)
            out_wav.setsampwidth(sampwidth)
            out_wav.setframerate(framerate)
            out_wav.setcomptype(comptype, "not compressed")

            for path in path_objs:
                with contextlib.closing(wave.open(str(path), "rb")) as in_wav:
                    out_wav.writeframes(in_wav.readframes(in_wav.getnframes()))

        return str(output_path)

    def synthesize_many(self, text: str, intent: str | None = None) -> List[str]:
        chunks = self._chunk_text(text)
        if not chunks:
            raise ValueError("No text provided for TTS synthesis.")

        audio_paths: List[str] = []
        for chunk in chunks:
            audio_paths.append(self._synthesize_chunk(chunk))

        return audio_paths

    def synthesize(self, text: str, intent: str | None = None) -> str:
        chunks = self._chunk_text(text)
        if not chunks:
            raise ValueError("No text provided for TTS synthesis.")

        if len(chunks) == 1:
            return self._synthesize_chunk(chunks[0])

        audio_paths = [self._synthesize_chunk(chunk) for chunk in chunks]
        return self._merge_wav_files(audio_paths)