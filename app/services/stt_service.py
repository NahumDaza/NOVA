from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


class WhisperCppSTTService:
    def __init__(self) -> None:
        self.whisper_dir = Path.home() / "whisper.cpp"
        self.binary = self.whisper_dir / "build" / "bin" / "whisper-cli"
        self.model = self.whisper_dir / "models" / "ggml-small.bin"

    def transcribe_file(self, audio_path: str, language: str = "es") -> str:
        if not self.binary.exists():
            raise FileNotFoundError(f"No encontré whisper-cli en {self.binary}")

        if not self.model.exists():
            raise FileNotFoundError(f"No encontré el modelo Whisper en {self.model}")

        wav_path = self._convert_to_wav(audio_path)

        cmd = [
            str(self.binary),
            "-m", str(self.model),
            "-f", wav_path,
            "-l", language,
            "-nt",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        transcript = self._extract_transcript(result.stdout)
        return transcript

    def save_temp_audio(self, raw_bytes: bytes, suffix: str = ".wav") -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(raw_bytes)
            return tmp.name

    def _convert_to_wav(self, input_path: str) -> str:
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name

        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            output_path,
        ]

        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        return output_path

    def _extract_transcript(self, stdout: str) -> str:
        lines = stdout.splitlines()
        spoken_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("[") and "]" in line:
                parts = line.split("]", maxsplit=1)
                if len(parts) == 2:
                    content = parts[1].strip()
                    if content:
                        spoken_lines.append(content)

        if spoken_lines:
            text = " ".join(spoken_lines).strip()
            return self._postprocess_text(text)

        return self._postprocess_text(stdout.strip())

    def _postprocess_text(self, text: str) -> str:
        cleaned = text.strip()

        noise_markers = {
            "[MÚSICA]",
            "[Música]",
            "[MUSICA]",
            "[Music]",
            "[SONIDO]",
            "[Noise]",
            "[Aplausos]",
        }

        if cleaned in noise_markers:
            return ""

        replacements = {
            "Hola nueva": "Hola Terra",
            "hola nueva": "Hola Terra",
            "Hola Nova": "Hola Terra",
            "hola Nova": "Hola Terra",
            "Hola no va": "Hola Terra",
            "hola no va": "Hola Terra",
            "Nova": "Terra",
            "NOVA": "Terra",
            "Tierra": "Terra",
            "tierra": "Terra",
            "La tierra fue tía": "Hola Terra, buen día",
            "la tierra fue tía": "Hola Terra, buen día",
            "Hola Terra como vas": "Hola Terra, ¿cómo vas?",
            "Hola Terra que tal todo": "Hola Terra, ¿qué tal todo?",
            "Hola Terra buen dia": "Hola Terra, buen día",
            "o la terra": "Hola Terra",
            "O la terra": "Hola Terra",
            "terra como más": "Terra, ¿cómo vas?",
            "Terra como más": "Terra, ¿cómo vas?",
            "terra como vas": "Terra, ¿cómo vas?",
            "Terra como vas": "Terra, ¿cómo vas?",
            "hola terra buen dia": "Hola Terra, buen día",
            "Hola terra buen dia": "Hola Terra, buen día",
            "correo breve para mi profesor porque falta clase": "correo breve para mi profesor porque falté a clase",
            "redacto un correo": "redacta un correo",
            "email": "correo",
            "clases": "clase",
        }

        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)

        cleaned = cleaned.strip()
        if cleaned.lower() in {"hola terra", "terra", "hola terra buen día", "terra, ¿cómo vas?"}:
            return cleaned

        return cleaned
    