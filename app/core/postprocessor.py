from __future__ import annotations


class ResponsePostProcessor:
    def clean(self, intent: str, response: str, language: str = "es") -> str:
        text = response.strip()

        if intent == "draft_message":
            text = self._clean_draft_message(text, language)

        return text.strip()

    def _clean_draft_message(self, text: str, language: str) -> str:
        replacements = {
            "Perdón por la ausencia y Consulta sobre Clase Faltada": "Inasistencia a clase",
            "Período de Falta por Ausencia en Clase": "Inasistencia a clase",
            "comprenderé cualquier sanción que esto pueda traerme.": "",
            "Lamento profundamente no haber asistido": "Lamento no haber asistido",
            "Le escribo para informarle que falté a la clase de [Nombre de la Clase] el día [Fecha].": (
                "Le escribo para informarle que no pude asistir a una de sus clases."
            ),
            "Le escribo para informarle que falté a la clase de [nombre del curso] el día [fecha].": (
                "Le escribo para informarle que no pude asistir a una de sus clases."
            ),
            "Si hay tareas o exámenes relacionados con la clase que falté, me gustaría saber cuándo y cómo puedo completarlos.": (
                "También le agradecería si me pudiera indicar si hubo material, actividades o tareas que deba revisar para ponerme al día."
            ),
            "[Nombre del Profesor]": "profesor",
            "[Nombre de la Clase]": "clase",
            "[Fecha]": "",
            "[Tu Nombre]": "Nahum",
            "Claro, aquí tienes un borrador del correo que puedes enviar a tu profesor:": "",
            "Aquí tienes un borrador del correo:": "",
            "Claro, aquí tienes el correo:": "",
        }

        cleaned = text
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)

        cleaned = cleaned.replace("Estimado profesor,", "Estimado profesor:")
        cleaned = cleaned.replace("Estimado Profesor,", "Estimado profesor:")
        cleaned = cleaned.replace("Atentamente,\n\nNahum", "Atentamente,\nNahum")
        cleaned = cleaned.replace("Atentamente,\n\n[Tu nombre]", "Atentamente,\nNahum")
        cleaned = cleaned.replace("Atentamente,\n[Tu nombre]", "Atentamente,\nNahum")

        while "\n\n\n" in cleaned:
            cleaned = cleaned.replace("\n\n\n", "\n\n")

        return cleaned