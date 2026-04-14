from __future__ import annotations

import re


class IntentRouter:
    def detect_intent(self, message: str) -> str:
        text = message.lower().strip()

        if self._is_refinement(text):
            return "refine_previous_output"

        if self._is_summary_request(text):
            return "summarize_text"

        if self._is_translation_request(text):
            return "translate_text"

        if self._is_rewrite_request(text):
            return "rewrite_text"

        # carpetas primero, antes de open_app
        if self._match_any(
            text,
            [
                "abre descargas",
                "abre descarga",
                "abre downloads",
                "abre documentos",
                "abre documento",
                "abre documents",
                "abre escritorio",
                "abre desktop",
                "abre proyectos",
                "abre project",
                "abre mi carpeta",
                "abre la carpeta",
            ],
        ):
            return "open_folder"

        if self._match_any(
            text,
            [
                "busca archivo",
                "busca el archivo",
                "encuentra archivo",
                "encuentra el archivo",
                "busca pdf",
                "busca documento",
            ],
        ):
            return "find_file"

        if self._match_any(
            text,
            [
                "abre el último archivo encontrado",
                "abre el ultimo archivo encontrado",
                "abre el archivo encontrado",
            ],
        ):
            return "open_found_file"
        
        if self._match_any(
            text,
            [
                "abre el último archivo encontrado",
                "abre el ultimo archivo encontrado",
                "abre el archivo encontrado",
                "ultimo archivo encontrado",
                "último archivo encontrado",
                "archivo encontrado",
            ],
        ):
            return "open_found_file"
        
        if self._match_any(text, ["lee el último archivo encontrado", "lee el ultimo archivo encontrado", "lee el archivo encontrado"]):
            return "read_last_found_file"

        if self._match_any(text, ["lee el archivo", "lee archivo", "lee el pdf", "leer archivo", "leer pdf"]):
            return "read_file"

        if self._match_any(text, ["lee este archivo", "lee el archivo activo", "resume este archivo", "resume este pdf"]):
            return "read_active_file"

        if self._match_any(text, ["archivo activo", "cuál es el archivo activo", "cual es el archivo activo"]):
            return "get_active_file"

        if self._match_any(text, ["abre", "open", "abrir"]):
            if any(x in text for x in ["archivo", ".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx"]):
                return "open_file"
            return "open_app"

        if self._match_any(text, ["copia", "copiar", "copy"]):
            return "copy_text"

        if self._match_any(text, ["nota", "guardar nota", "take note"]):
            return "save_note"

        if self._match_any(text, ["tarea", "recordatorio", "todo"]):
            return "save_task"

        if self._match_any(
            text,
            [
                "draft",
                "email",
                "correo",
                "reply",
                "redacta",
                "escribe un correo",
                "redactar un correo",
                "escribe un email",
                "redacta un email",
            ],
        ):
            return "draft_message"

        if self._match_any(
            text,
            [
                "organize",
                "organiza",
                "priorities",
                "pendientes",
                "organiza mi día",
                "organiza mi dia",
                "mi agenda",
            ],
        ):
            return "organize_day"

        if self._match_math(text):
            return "calculate_math"

        if self._match_any(
            text,
            [
                "physics",
                "física",
                "velocity",
                "force",
                "aceleración",
                "velocidad",
            ],
        ):
            return "solve_physics"

        if self._match_any(
            text,
            [
                "chemistry",
                "química",
                "molar",
                "reaction",
                "reacción",
            ],
        ):
            return "solve_chemistry"

        if self._match_any(
            text,
            [
                "process",
                "workflow",
                "estructura",
                "strategy",
                "proceso",
                "estrategia",
            ],
        ):
            return "think_process"

        if self._looks_like_english(text):
            return "improve_english"

        return "general_chat"

    def _match_any(self, text: str, keywords: list[str]) -> bool:
        return any(word in text for word in keywords)

    def _match_math(self, text: str) -> bool:
        return bool(re.search(r"[0-9x\+\-\*/=]", text)) and not self._is_refinement(text)

    def _looks_like_english(self, text: str) -> bool:
        patterns = [
            r"correct my english",
            r"is this correct",
            r"my english",
            r"i didn.?t",
            r"he don.?t",
        ]
        return any(re.search(p, text) for p in patterns)

    def _is_refinement(self, text: str) -> bool:
        refinement_patterns = [
            "hazlo más formal",
            "hazlo mas formal",
            "hazlo más breve",
            "hazlo mas breve",
            "hazlo más corto",
            "hazlo mas corto",
            "mejóralo",
            "mejoralo",
            "refínalo",
            "refinalo",
            "tradúcelo",
            "traducelo",
            "ponlo en inglés",
            "ponlo en ingles",
            "make it more formal",
            "make it shorter",
            "make it brief",
            "improve it",
            "refine it",
            "translate it",
        ]
        return any(pattern in text for pattern in refinement_patterns)

    def _is_summary_request(self, text: str) -> bool:
        patterns = [
            "resume esto",
            "resúmelo",
            "resumelo",
            "hazme un resumen",
            "haz un resumen",
            "resúmeme",
            "resumeme",
            "summarize",
            "summary",
        ]
        return any(pattern in text for pattern in patterns)

    def _is_translation_request(self, text: str) -> bool:
        patterns = [
            "traduce esto",
            "traducir esto",
            "translate this",
            "translate to english",
            "translate to spanish",
            "pásalo a inglés",
            "pasalo a ingles",
            "pásalo a español",
            "pasalo a español",
            "pásalo al inglés",
            "pasalo al ingles",
        ]
        return any(pattern in text for pattern in patterns)

    def _is_rewrite_request(self, text: str) -> bool:
        patterns = [
            "reescribe esto",
            "reescríbelo",
            "reescribelo",
            "rewrite this",
            "rephrase this",
            "ponlo más profesional",
            "ponlo mas profesional",
            "hazlo más ejecutivo",
            "hazlo mas ejecutivo",
            "hazlo más casual",
            "hazlo mas casual",
            "hazlo más claro",
            "hazlo mas claro",
        ]
        return any(pattern in text for pattern in patterns)