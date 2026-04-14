from __future__ import annotations

import contextlib
import re
import subprocess
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

        self.clips_dir = Path("/Users/macuser/nova-audio/clips")

        self.clip_map = {
            "claro": "claro.mp3",
            "perfecto": "perfecto.mp3",
            "listo jefe": "listo_jefe.mp3",
            "que necesitas": "que_necesitas.mp3",
            "todo en orden": "todo_en_orden.mp3",
            "aqui estoy": "aqui_estoy.mp3",
            "abri la carpeta": "abri_la_carpeta.mp3",
            "abri la aplicacion": "abri_la_aplicacion.mp3",
            "guarde la nota": "guarde_la_nota.mp3",
            "guarde la tarea": "guarde_la_tarea.mp3",
            "preparado": "preparado.mp3",
            "en orden": "en_orden.mp3",
            "hecho": "hecho.mp3",
            "listo": "listo.mp3",
            "hola nahum": "hola_nahum.mp3",
            "hola jefe": "hola_jefe.mp3",
            "buenos dias nahum": "buenos_dias_nahum.mp3",
            "buenos dias jefe": "buenos_dias_jefe.mp3",
            "buenas tardes nahum": "buenas_tardes_nahum.mp3",
            "buenas tardes jefe": "buenas_tardes_jefe.mp3",
            "bienvenido de nuevo nahum": "bienvenido_nahum.mp3",
            "bienvenido de nuevo jefe": "bienvenido_jefe.mp3",
            "como vas": "como_vas.mp3",
            "como estas": "como_estas.mp3",
            "todo bien por aqui": "todo_bien.mp3",
            "en orden jefe": "en_orden_jefe.mp3",
            "listo nahum": "listo_nahum.mp3",
            "en que te ayudo": "en_que_te_ayudo.mp3",
            "como va tu dia": "como_va_tu_dia.mp3",
            "todo bien por aqui nahum": "todo_bien_nahum.mp3",
            "buenos dias jefe que necesitas": "buenos_dias_jefe_que_necesitas.mp3",
            "buenos dias nahum que necesitas": "buenos_dias_nahum_que_necesitas.mp3",
            "buenas tardes jefe que necesitas": "buenas_tardes_jefe_que_necesitas.mp3",
            "buenas tardes nahum que necesitas": "buenas_tardes_nahum_que_necesitas.mp3",
            "hola jefe en que te ayudo": "hola_jefe_en_que_te_ayudo.mp3",
            "hola nahum como vas": "hola_nahum_como_vas.mp3",
            "bienvenido de nuevo jefe que necesitas": "bienvenido_jefe_que_necesitas.mp3",
            "bienvenido de nuevo nahum como vas": "bienvenido_nahum_como_vas.mp3",

            "todo bien por aqui que necesitas": "todo_bien_que_necesitas.mp3",
            "aqui estoy en que te ayudo": "aqui_estoy_en_que_te_ayudo.mp3",
            "todo en orden como va tu dia": "todo_en_orden_como_va_tu_dia.mp3",
            "estoy bien como vas": "estoy_bien_como_vas.mp3",
            "estoy bien como vas tu": "estoy_bien_como_vas_tu.mp3",
            "todo bien por aqui nahum": "todo_bien_nahum.mp3",

            "prepare el correo para tu profesor": "correo_preparado.mp3",
            "hice el ajuste": "ajuste_realizado.mp3",
            "ya deje la traduccion lista": "traduccion_lista.mp3",
            "ya prepare el resumen": "resumen_preparado.mp3",
            "ya ajuste el texto": "texto_ajustado.mp3",
            "lo copie": "lo_copie.mp3",

            "y listo": "y_listo.mp3",
            "y ya quedo": "y_ya_quedo.mp3",
            "listo ya": "listo_ya.mp3",
            "vamos a ello": "vamos_a_ello.mp3",
            "un momento": "un_momento.mp3",

            "no encontre archivos con ese nombre": "no_encontre_archivos.mp3",
            "no identifique la aplicacion que quieres abrir": "no_identifique_la_aplicacion.mp3",
            "no identifique la carpeta que quieres abrir": "no_identifique_la_carpeta.mp3",
            "no te escuche bien intenta otra vez": "no_te_escuche_bien.mp3",
        }

    def _clean_text(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _normalize_for_clip_match(self, text: str) -> str:
        cleaned = text.lower().strip()

        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ü": "u",
            "¿": "",
            "?": "",
            "¡": "",
            "!": "",
            ".": "",
            ",": "",
            ":": "",
            ";": "",
        }

        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)

        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def _get_clip_for_text(self, text: str) -> str | None:
        normalized = self._normalize_for_clip_match(text)

        if normalized in self.clip_map:
            candidate = self.clips_dir / self.clip_map[normalized]
            if candidate.exists():
                return str(candidate)

        return None

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

    def _validate_wav_compatibility(self, wav_paths: List[Path]) -> tuple[int, int, int, str]:
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
                raise ValueError(f"Expected WAV files for merge, but got: {path.name}")
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

    def _convert_to_wav(self, input_path: str) -> str:
        input_file = Path(input_path)
        output_path = self.output_dir / f"clip_{uuid.uuid4().hex}.wav"

        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_file),
            "-ar", "24000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            str(output_path),
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return str(output_path)

    def _concat_audio_files(self, audio_paths: List[str]) -> str:
        if not audio_paths:
            raise ValueError("No audio files provided for concatenation.")

        wav_paths = [self._convert_to_wav(path) for path in audio_paths]
        return self._merge_wav_files(wav_paths)

    def _build_audio_sequence(self, text: str) -> List[str]:
        sentences = self._split_into_sentences(text)
        if not sentences:
            raise ValueError("No text provided for TTS synthesis.")

        audio_parts: List[str] = []

        for sentence in sentences:
            clip = self._get_clip_for_text(sentence)
            if clip:
                audio_parts.append(clip)
                continue

            chunks = self._chunk_text(sentence)
            for chunk in chunks:
                audio_parts.append(self._synthesize_chunk(chunk))

        return audio_parts

    def synthesize_many(self, text: str, intent: str | None = None) -> List[str]:
        return self._build_audio_sequence(text)

    def synthesize(self, text: str, intent: str | None = None) -> str:
        audio_parts = self._build_audio_sequence(text)

        if len(audio_parts) == 1:
            return audio_parts[0]

        return self._concat_audio_files(audio_parts)

    def synthesize_with_prefix(
        self,
        prefix_text: str | None,
        main_text: str,
        intent: str | None = None,
    ) -> str:
        parts: List[str] = []

        prefix_text = self._clean_text(prefix_text or "")
        main_text = self._clean_text(main_text)

        if prefix_text:
            parts.append(prefix_text)

        if main_text:
            parts.append(main_text)

        merged_text = " ".join(parts).strip()
        if not merged_text:
            raise ValueError("No text provided for synthesize_with_prefix.")

        return self.synthesize(merged_text, intent=intent)