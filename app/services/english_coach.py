import re


class EnglishCoach:
    def maybe_correct(self, message: str, language: str = "auto") -> str | None:
        text = message.lower()

        corrections = []

        if re.search(r"i didn.?t went", text):
            corrections.append(
                "It should be 'I didn't go,' not 'I didn't went.' After 'didn't,' the verb stays in base form."
            )

        if re.search(r"he don.?t", text):
            corrections.append(
                "It should be 'he doesn't,' not 'he don't.' Third-person singular requires 'doesn't.'"
            )

        if re.search(r"i have \d+ years", text):
            corrections.append(
                "In English we say 'I am X years old,' not 'I have X years.'"
            )

        if corrections:
            return "Correction: " + " ".join(corrections)

        return None