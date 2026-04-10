import re


class EnglishCoach:
    def maybe_correct(self, message: str, language: str = "auto") -> str | None:
        text = message.lower()

        corrections = []

        if re.search(r"i didn.?t went", text):
            corrections.append(
                "Se dice 'I didn't go', no 'I didn't went', porque después de 'didn't' el verbo debe ir en su forma base."
            )

        if re.search(r"he don.?t", text):
            corrections.append(
                "Se dice 'he doesn't', no 'he don't', porque en tercera persona singular se usa 'doesn't'."
            )

        if re.search(r"i have \d+ years", text):
            corrections.append(
                "En inglés se dice 'I am X years old', no 'I have X years'."
            )

        if corrections:
            return "Corrección rápida: " + " ".join(corrections)

        return None