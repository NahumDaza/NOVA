from __future__ import annotations

import httpx


class XTTSService:
    def __init__(self) -> None:
        self.base_url = "http://127.0.0.1:8010"

    def synthesize(self, text: str, intent: str | None = None) -> str:
        spoken_version = self._make_spoken_version(text, intent)

        response = httpx.post(
            f"{self.base_url}/synthesize",
            json={
                "text": spoken_version,
                "language": "es",
            },
            timeout=300.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["audio_path"]

    def _make_spoken_version(self, text: str, intent: str | None = None) -> str:
        if intent == "draft_message":
            return (
                "Listo. Ya preparé un correo breve para tu profesor informando que no pudiste asistir a clase "
                "y solicitando el material para ponerte al día. "
                "Si quieres, ahora lo hago más formal, más corto o lo traduzco."
            )

        if intent == "no_speech_detected":
            return "No detecté tu voz con suficiente claridad. Intenta hablar un poco más cerca del micrófono."

        cleaned = text.strip()

        if len(cleaned) > 220:
            cleaned = cleaned[:220].rsplit(" ", 1)[0].strip() + "."

        return cleaned