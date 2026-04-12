from __future__ import annotations

import httpx

from app.core.terra_persona import TerraPersona


class XTTSService:
    def __init__(self) -> None:
        self.base_url = "http://127.0.0.1:8010"
        self.persona = TerraPersona()

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
            return self.persona.draft_message_voice_line()

        if intent == "no_speech_detected":
            return self.persona.no_speech_line()

        cleaned = text.strip()

        if len(cleaned) > 160:
            cleaned = cleaned[:160].rsplit(" ", 1)[0].strip() + "."

        return cleaned