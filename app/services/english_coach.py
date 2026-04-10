class EnglishCoach:
    def maybe_correct(self, message: str, language: str = "auto") -> str | None:
        lower = message.lower()

        if "i didn't went" in lower:
            return (
                "Quick correction: it should be 'I didn't go,' not 'I didn't went.' "
                "After 'didn't,' the verb stays in base form."
            )

        if "he don't" in lower:
            return (
                "Quick correction: it should be 'he doesn't,' not 'he don't.' "
                "Third-person singular in the present takes 'doesn't.'"
            )

        return None