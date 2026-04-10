from __future__ import annotations

import os
from typing import Protocol

from dotenv import load_dotenv

from app.prompts.system_prompt import NOVA_SYSTEM_PROMPT

load_dotenv()


class LLMProvider(Protocol):
    def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        ...

    def refine_text(
        self,
        original_text: str,
        instruction: str,
        language: str = "es",
    ) -> str:
        ...


class PlaceholderProvider:
    def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        history = history or []
        context = " | ".join([f"{m['role']}: {m['content']}" for m in history[-4:]])

        return (
            "LLM placeholder activo. "
            f"Mensaje actual: {user_message}. "
            f"Contexto reciente: {context if context else 'sin contexto'}."
        )

    def refine_text(
        self,
        original_text: str,
        instruction: str,
        language: str = "es",
    ) -> str:
        return (
            f"[PLACEHOLDER]\nInstrucción: {instruction}\n\n"
            f"Texto base:\n{original_text}"
        )


class OpenAIProvider:
    def __init__(self) -> None:
        from openai import OpenAI

        self.client = OpenAI()
        self.model = os.getenv("OPENAI_MODEL", "gpt-5")

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        history = history or []

        input_items: list[dict[str, str]] = []
        for item in history[-6:]:
            input_items.append(
                {
                    "role": item["role"],
                    "content": item["content"],
                }
            )

        input_items.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=input_items,
        )
        return response.output_text.strip()

    def refine_text(
        self,
        original_text: str,
        instruction: str,
        language: str = "es",
    ) -> str:
        response_language = "español" if language.startswith("es") else "English"

        response = self.client.responses.create(
            model=self.model,
            instructions=(
                f"{NOVA_SYSTEM_PROMPT}\n\n"
                "Tu tarea es refinar un texto existente.\n"
                "Debes mantener la intención original y aplicar únicamente la instrucción dada.\n"
                f"Responde en {response_language}.\n"
                "Devuelve solo el texto final refinado, sin explicación adicional."
            ),
            input=(
                f"Instrucción del usuario:\n{instruction}\n\n"
                f"Texto original:\n{original_text}"
            ),
        )
        return response.output_text.strip()


class LLMService:
    def __init__(self) -> None:
        provider_name = os.getenv("NOVA_LLM_PROVIDER", "openai").lower()

        if provider_name == "openai":
            try:
                self.provider: LLMProvider = OpenAIProvider()
            except Exception:
                self.provider = PlaceholderProvider()
        else:
            self.provider = PlaceholderProvider()

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        return self.provider.generate(
            system_prompt=system_prompt,
            user_message=user_message,
            history=history,
        )

    def refine_text(
        self,
        original_text: str,
        instruction: str,
        language: str = "es",
    ) -> str:
        return self.provider.refine_text(
            original_text=original_text,
            instruction=instruction,
            language=language,
        )