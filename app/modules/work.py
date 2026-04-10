class WorkModule:
    def organize_day(self, message: str) -> str:
        return (
            "Entendido. Para esta V1 todavía no estoy conectado a tu calendario ni a tus correos, "
            "pero ya puedo ayudarte a estructurar el día. Propón tus 3 pendientes más importantes "
            "y te los ordeno por impacto, urgencia y secuencia recomendada."
        )

    def general_assist(self, message: str) -> str:
        return (
            "Te entendí. En esta primera versión puedo ayudarte a organizar trabajo, redactar, "
            "pensar procesos, corregir inglés y resolver cálculos técnicos."
        )