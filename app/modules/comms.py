class CommsModule:
    def draft_message(self, message: str) -> str:
        text = message.lower()

        if "profesor" in text or "teacher" in text:
            return (
                "Hola, profesor.\n\n"
                "Espero que se encuentre bien. Le escribo para informarle que no pude asistir a clase.\n\n"
                "Quedo atento y gracias por su comprensión.\n"
            )

        if "cliente" in text or "customer" in text:
            return (
                "Hola,\n\n"
                "Espero que se encuentre bien. Le escribo para dar seguimiento a este tema y mantenerle al tanto.\n\n"
                "Quedo atento.\n"
            )

        return (
            "Hola,\n\n"
            "Le escribo para comunicarle este asunto.\n\n"
            "Quedo atento.\n"
        )