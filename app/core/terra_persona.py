from __future__ import annotations

import random
from typing import Optional


class TerraPersona:
    def __init__(self) -> None:
        self.greetings = [
            "Hola, Nahum.",
            "Bienvenido de nuevo, Nahum.",
            "Aquí estoy, jefe.",
            "Todo en orden, jefe.",
            "Buen regreso, Nahum.",
            "Hola, jefe.",
            "En orden, Nahum.",
        ]

        self.confirmations = [
            "Hecho.",
            "Ya quedó listo.",
            "Listo.",
            "En orden.",
            "Preparado.",
            "Lo tengo.",
        ]

        self.follow_ups = [
            "Lo ajusto si quieres.",
            "Puedo afinarlo.",
            "Lo adapto enseguida.",
            "También puedo traducirlo.",
            "",
        ]

    def _pick_different(self, options: list[str], last_used: Optional[str]) -> str:
        candidates = [opt for opt in options if opt != last_used]
        if not candidates:
            candidates = options
        return random.choice(candidates)

    def greeting(self, last_used: Optional[str] = None) -> str:
        return self._pick_different(self.greetings, last_used)

    def confirmation(self, last_used: Optional[str] = None) -> str:
        return self._pick_different(self.confirmations, last_used)

    def follow_up(self, last_used: Optional[str] = None) -> str:
        return self._pick_different(self.follow_ups, last_used)

    def draft_message_voice_line(
        self,
        last_confirmation: Optional[str] = None,
        last_follow_up: Optional[str] = None,
    ) -> str:
        confirmation = self.confirmation(last_confirmation)
        follow_up = self.follow_up(last_follow_up)

        if follow_up:
            return f"{confirmation} Preparé el correo para tu profesor. {follow_up}".strip()

        return f"{confirmation} Preparé el correo para tu profesor.".strip()

    def no_speech_line(self) -> str:
        return "No te escuché con claridad. Intenta otra vez."