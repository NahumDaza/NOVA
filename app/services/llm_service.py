class LLMService:
    def generate(self, system_prompt: str, user_message: str, history: list[dict[str, str]] | None = None) -> str:
        history = history or []
        context = " | ".join([f"{m['role']}: {m['content']}" for m in history[-4:]])

        return (
            "LLM placeholder activo. "
            f"Mensaje actual: {user_message}. "
            f"Contexto reciente: {context if context else 'sin contexto'}."
        )