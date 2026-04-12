from __future__ import annotations

from app.prompts.system_prompt import NOVA_SYSTEM_PROMPT
from app.services.llm_service import LLMService


class TextToolsModule:
    def __init__(self) -> None:
        self.llm = LLMService()

    def summarize(self, message: str, language: str = "es") -> str:
        prompt = (
            f"{NOVA_SYSTEM_PROMPT}\n\n"
            "Resume el contenido de forma clara, breve y útil.\n"
            "Entrega directamente el resumen.\n"
        )
        return self.llm.generate(
            system_prompt=prompt,
            user_message=message,
            history=[],
        )

    def translate(self, message: str, language: str = "es") -> str:
        prompt = (
            f"{NOVA_SYSTEM_PROMPT}\n\n"
            "Tu tarea es traducir el contenido solicitado.\n"
            "Entrega directamente la traducción final, sin explicaciones adicionales.\n"
        )
        return self.llm.generate(
            system_prompt=prompt,
            user_message=message,
            history=[],
        )

    def rewrite(self, message: str, language: str = "es") -> str:
        prompt = (
            f"{NOVA_SYSTEM_PROMPT}\n\n"
            "Tu tarea es reescribir o mejorar el texto solicitado.\n"
            "Entrega directamente la versión final.\n"
        )
        return self.llm.generate(
            system_prompt=prompt,
            user_message=message,
            history=[],
        )