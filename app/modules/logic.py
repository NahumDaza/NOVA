from sympy import Eq, Symbol, sympify, solve


class LogicModule:
    def solve(self, message: str, intent: str) -> str:
        if intent == "calculate_math":
            return self._solve_basic_math(message)

        if intent == "solve_physics":
            return (
                "Puedo ayudarte con física. En la siguiente versión agregaré parser de variables, "
                "unidades y fórmulas típicas de cinemática y dinámica."
            )

        if intent == "solve_chemistry":
            return (
                "Puedo ayudarte con química. En la siguiente versión agregaré conversiones molares, "
                "masa molar y estequiometría básica."
            )

        return "No pude clasificar el cálculo solicitado."

    def _solve_basic_math(self, message: str) -> str:
        text = message.strip().lower()
        text = text.replace("solve", "").replace("resuelve", "").strip()

        if "=" not in text:
            return "Pásame una ecuación simple, por ejemplo: x + 2 = 5."

        left, right = text.split("=", maxsplit=1)
        x = Symbol("x")
        equation = Eq(sympify(left), sympify(right))
        result = solve(equation, x)
        return f"Resultado: x = {result[0]}" if result else "No encontré una solución para esa ecuación."