class LLMService:
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
        instruction_lower = instruction.lower()

        refined = original_text

        if "más formal" in instruction_lower or "mas formal" in instruction_lower or "more formal" in instruction_lower:
            refined = self._make_more_formal(refined, language)

        if (
            "más breve" in instruction_lower
            or "mas breve" in instruction_lower
            or "más corto" in instruction_lower
            or "mas corto" in instruction_lower
            or "shorter" in instruction_lower
            or "brief" in instruction_lower
        ):
            refined = self._make_shorter(refined)

        if "tradúcelo" in instruction_lower or "traducelo" in instruction_lower or "translate" in instruction_lower:
            refined = self._translate_placeholder(refined, instruction_lower)

        return refined

    def _make_more_formal(self, text: str, language: str) -> str:
        if language == "es":
            return text.replace("Hola,", "Estimado profesor,").replace("Gracias.", "Muchas gracias por su atención.")
        return text.replace("Hi,", "Dear Professor,").replace("Thanks.", "Thank you for your time and consideration.")

    def _make_shorter(self, text: str) -> str:
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        shortened = ". ".join(sentences[:2]).strip()
        return shortened + "." if shortened and not shortened.endswith(".") else shortened

    def _translate_placeholder(self, text: str, instruction: str) -> str:
        if "inglés" in instruction or "ingles" in instruction or "english" in instruction:
            return (
                "Dear Professor,\n\n"
                "I hope you are doing well. I am writing to let you know that I was unable to attend class.\n\n"
                "Thank you for your understanding.\n"
            )
        return text