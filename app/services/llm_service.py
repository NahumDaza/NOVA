from __future__ import annotations

import os
from typing import Protocol

from dotenv import load_dotenv
import httpx

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
        return f"[PLACEHOLDER]\nInstrucción: {instruction}\n\nTexto base:\n{original_text}"


class LMStudioProvider:
    def __init__(self) -> None:
        self.base_url = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
        self.model = os.getenv("LMSTUDIO_MODEL", "qwen2.5-7b-instruct-mlx")
        self.timeout = 180.0

    def _chat_completion(self, messages: list[dict[str, str]]) -> str:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0.4,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        history = history or []

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
        messages.extend(history[-6:])
        messages.append({"role": "user", "content": user_message})

        return self._chat_completion(messages)

    def refine_text(
        self,
        original_text: str,
        instruction: str,
        language: str = "es",
    ) -> str:
        response_language = "español" if language.startswith("es") else "English"

        messages = [
            {
                "role": "system",
                "content": (
                    f"{NOVA_SYSTEM_PROMPT}\n\n"
                    "Tu tarea es refinar un texto existente.\n"
                    "Mantén la intención original.\n"
                    "Aplica únicamente la instrucción dada.\n"
                    f"Responde en {response_language}.\n"
                    "Devuelve solo el texto final refinado."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Instrucción del usuario:\n{instruction}\n\n"
                    f"Texto original:\n{original_text}"
                ),
            },
        ]

        return self._chat_completion(messages)


class LLMService:
    def __init__(self) -> None:
        provider_name = os.getenv("NOVA_LLM_PROVIDER", "lmstudio").lower()

        if provider_name == "lmstudio":
            try:
                self.provider: LLMProvider = LMStudioProvider()
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