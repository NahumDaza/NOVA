from __future__ import annotations

import httpx


class XTTSService:
    def __init__(self) -> None:
        self.base_url = "http://127.0.0.1:8010"

    def synthesize(self, text: str, intent: str | None = None) -> str:
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
        return data["audio_path"]