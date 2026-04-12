from __future__ import annotations

import httpx


class XTTSService:
    def __init__(self) -> None:
        self.base_url = "http://127.0.0.1:8010"

    def synthesize(self, text: str) -> str:
        spoken_version = self._make_spoken_version(text)

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

    def _make_spoken_version(self, text: str) -> str:
        cleaned = text.strip()

        if "Asunto:" in cleaned and "Atentamente" in cleaned:
            return (
                "Listo. Ya preparé el correo. "
                "Si quieres, puedo hacerlo más breve, más formal o traducirlo."
            )

        if len(cleaned) > 280:
            return cleaned[:280].rsplit(" ", 1)[0].strip() + "."

        return cleaned