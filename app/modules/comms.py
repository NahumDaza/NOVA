from __future__ import annotations

from app.prompts.system_prompt import NOVA_SYSTEM_PROMPT
from app.services.llm_service import LLMService


class CommsModule:
    def __init__(self) -> None:
        self.llm = LLMService()

    def draft_message(self, message: str, language: str = "es") -> str:
        response_language = "español" if language.startswith("es") else "English"

        prompt = (
            f"{NOVA_SYSTEM_PROMPT}\n\n"
            "Tu tarea es redactar un borrador útil y listo para revisión.\n"
            "- Si el usuario pide un correo, redacta un correo real.\n"
            "- No expliques lo que vas a hacer.\n"
            "- Entrega directamente el borrador.\n"
            "- Usa un tono apropiado al contexto.\n"
            "- Si faltan datos, asume una versión prudente y profesional.\n"
            f"- Responde en {response_language}.\n"
        )

        return self.llm.generate(
            system_prompt=prompt,
            user_message=message,
            history=[],
        )