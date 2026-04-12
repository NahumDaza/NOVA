from __future__ import annotations

from app.prompts.system_prompt import NOVA_SYSTEM_PROMPT
from app.services.llm_service import LLMService


class CommsModule:
    def __init__(self) -> None:
        self.llm = LLMService()

    def draft_message(self, message: str, language: str = "es") -> str:
        text = message.lower()

        if self._is_absence_to_teacher_case(text):
            return self._draft_absence_to_teacher()

        response_language = "español" if language.startswith("es") else "English"

        prompt = (
            f"{NOVA_SYSTEM_PROMPT}\n\n"
            "Tu tarea es redactar un borrador útil y listo para revisión.\n"
            "- Si el usuario pide un correo, redacta un correo real.\n"
            "- No expliques lo que vas a hacer.\n"
            "- Entrega directamente el borrador.\n"
            "- Usa un tono apropiado al contexto.\n"
            "- Si faltan datos, asume una versión prudente y profesional.\n"
            "- Evita placeholders innecesarios.\n"
            "- Mantén la respuesta breve y lista para usar.\n"
            f"- Responde en {response_language}.\n"
        )

        return self.llm.generate(
            system_prompt=prompt,
            user_message=message,
            history=[],
        )

    def _is_absence_to_teacher_case(self, text: str) -> bool:
        teacher_words = ["profesor", "profesora", "teacher"]
        absence_words = [
            "falté", "falte", "ausencia", "no pude asistir", "no asistí",
            "no asisti", "perdí la clase", "perdi la clase", "me perdí la clase",
            "me perdi la clase", "falté a clase", "falte a clase"
        ]
        class_words = ["clase", "curso", "materia"]

        return (
            any(word in text for word in teacher_words)
            and any(word in text for word in absence_words)
            and any(word in text for word in class_words)
        )

    def _draft_absence_to_teacher(self) -> str:
        return (
            "Asunto: Inasistencia a clase\n\n"
            "Estimado profesor:\n\n"
            "Le escribo para informarle que no pude asistir a una de sus clases por un inconveniente personal.\n\n"
            "Le agradecería si me pudiera indicar el material visto, así como cualquier actividad o tarea que deba revisar para ponerme al día.\n\n"
            "Gracias por su comprensión.\n\n"
            "Atentamente,\n"
            "Nahum Daza"
        )