from __future__ import annotations

import random


class TerraPersona:
    def __init__(self) -> None:
        self.greetings = [
            "Hola, Nahum.",
            "Bienvenido de nuevo, Nahum.",
            "Aquí estoy, jefe.",
            "Todo en orden, jefe.",
            "Buen regreso, Nahum.",
        ]

        self.confirmations = [
            "Entendido.",
            "Hecho.",
            "Ya quedó listo.",
            "Está preparado.",
            "Lo tengo.",
            "En orden.",
        ]

        self.follow_ups = [
            "Lo ajusto si quieres.",
            "Puedo afinarlo.",
            "Lo dejo más breve si quieres.",
            "También puedo traducirlo.",
            "Lo adapto enseguida.",
        ]

    def greeting(self) -> str:
        return random.choice(self.greetings)

    def confirmation(self) -> str:
        return random.choice(self.confirmations)

    def follow_up(self) -> str:
        return random.choice(self.follow_ups)

    def draft_message_voice_line(self) -> str:
        return f"{self.confirmation()} Preparé el correo para tu profesor. {self.follow_up()}"

    def no_speech_line(self) -> str:
        return "No te escuché con claridad. Intenta otra vez."