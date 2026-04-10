import re


class IntentRouter:
    def detect_intent(self, message: str) -> str:
        text = message.lower().strip()

        # --- prioridad alta (acciones claras) ---
        if self._match_any(text, ["draft", "email", "correo", "reply", "redacta"]):
            return "draft_message"

        if self._match_any(text, ["organize", "organiza", "priorities", "pendientes"]):
            return "organize_day"

        # --- lógica / ciencia ---
        if self._match_math(text):
            return "calculate_math"

        if self._match_any(text, ["physics", "física", "velocity", "force"]):
            return "solve_physics"

        if self._match_any(text, ["chemistry", "química", "molar", "reaction"]):
            return "solve_chemistry"

        # --- pensamiento estructural ---
        if self._match_any(text, ["process", "workflow", "estructura", "strategy"]):
            return "think_process"

        # --- inglés ---
        if self._looks_like_english(text):
            return "improve_english"

        return "general_chat"

    def _match_any(self, text: str, keywords: list[str]) -> bool:
        return any(word in text for word in keywords)

    def _match_math(self, text: str) -> bool:
        return bool(re.search(r"[0-9x\+\-\*/=]", text))

    def _looks_like_english(self, text: str) -> bool:
        patterns = [
            r"correct my english",
            r"is this correct",
            r"my english",
            r"i didn.?t",
            r"he don.?t",
        ]
        return any(re.search(p, text) for p in patterns)