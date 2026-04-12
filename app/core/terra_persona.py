from __future__ import annotations

import random
from datetime import datetime
from typing import Optional

from app.core.terra_state import TerraConversationState


class TerraPersona:
    def __init__(self) -> None:
        self.morning_greetings = [
            "Buenos días, Nahum.",
            "Buenos días, jefe.",
            "Buen día, Nahum.",
        ]

        self.afternoon_greetings = [
            "Buenas tardes, Nahum.",
            "Buenas tardes, jefe.",
            "Hola, Nahum.",
        ]

        self.evening_greetings = [
            "Buenas noches, Nahum.",
            "Buenas noches, jefe.",
            "Hola, Nahum.",
        ]

        self.return_greetings = [
            "Bienvenido de nuevo, Nahum.",
            "Bienvenido de nuevo, jefe.",
            "De vuelta, Nahum.",
            "Qué bueno tenerte de regreso, jefe.",
        ]

        self.neutral_greetings = [
            "Aquí estoy, Nahum.",
            "Aquí estoy, jefe.",
            "Todo en orden, Nahum.",
            "Todo en orden, jefe.",
            "Listo, Nahum.",
        ]

        self.confirmations = [
            "Hecho.",
            "Ya quedó listo.",
            "Listo.",
            "En orden.",
            "Preparado.",
            "Lo tengo.",
        ]

        self.followups = [
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

    def greeting_for_context(self, state: TerraConversationState) -> str:
        now = datetime.now()
        hour = now.hour

        if state.last_interaction_at is not None:
            seconds_away = (now - state.last_interaction_at).total_seconds()
            if seconds_away >= 180:
                return self._pick_different(self.return_greetings, state.last_greeting)

        if hour < 12:
            return self._pick_different(self.morning_greetings, state.last_greeting)
        if hour < 19:
            return self._pick_different(self.afternoon_greetings, state.last_greeting)
        return self._pick_different(self.evening_greetings, state.last_greeting)

    def neutral_greeting(self, state: TerraConversationState) -> str:
        return self._pick_different(self.neutral_greetings, state.last_greeting)

    def confirmation(self, state: TerraConversationState) -> str:
        return self._pick_different(self.confirmations, state.last_confirmation)

    def followup(self, state: TerraConversationState) -> str:
        return self._pick_different(self.followups, state.last_followup)