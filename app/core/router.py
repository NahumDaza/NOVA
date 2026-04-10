import re


class IntentRouter:
    def detect_intent(self, message: str) -> str:
        text = message.lower().strip()

        if any(word in text for word in ["organiza mi día", "organize my day", "prioridades", "priorities"]):
            return "organize_day"

        if any(word in text for word in ["correo", "email", "draft", "redacta", "reply"]):
            return "draft_message"

        if any(word in text for word in ["derivada", "integral", "ecuación", "equation", "solve", "calculate"]):
            return "calculate_math"

        if any(word in text for word in ["física", "physics", "velocity", "force", "acceleration"]):
            return "solve_physics"

        if any(word in text for word in ["química", "chemistry", "molar", "stoichiometry", "estequiometría"]):
            return "solve_chemistry"

        if any(word in text for word in ["proceso", "process", "workflow", "estructura", "strategy"]):
            return "think_process"

        if self._looks_like_english_coaching(text):
            return "improve_english"

        return "general_chat"

    def _looks_like_english_coaching(self, text: str) -> bool:
        patterns = [
            r"correct my english",
            r"is this english correct",
            r"corrige mi inglés",
            r"my english",
        ]
        return any(re.search(pattern, text) for pattern in patterns)