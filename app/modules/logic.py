from sympy import symbols, Eq, sympify, solve, diff, integrate


class LogicModule:
    def solve(self, message: str, intent: str) -> str:
        text = message.lower().replace("solve", "").replace("resuelve", "").strip()

        # ecuaciones
        if "=" in text:
            return self._solve_equation(text)

        # derivadas
        if "derivative" in text or "derivada" in text:
            return self._derivative(text)

        # integrales
        if "integral" in text:
            return self._integral(text)

        # expresión directa
        return self._evaluate_expression(text)

    def _solve_equation(self, text: str) -> str:
        try:
            left, right = text.split("=")
            x = symbols("x")
            eq = Eq(sympify(left), sympify(right))
            result = solve(eq, x)
            return f"Resultado: x = {result[0]}" if result else "Sin solución encontrada."
        except Exception:
            return "No pude resolver la ecuación. Verifica el formato."

    def _evaluate_expression(self, text: str) -> str:
        try:
            result = sympify(text)
            return f"Resultado: {result}"
        except Exception:
            return "No pude interpretar la expresión matemática."

    def _derivative(self, text: str) -> str:
        try:
            x = symbols("x")
            expr = sympify(text.replace("derivative of", "").replace("derivada de", ""))
            return f"Derivada: {diff(expr, x)}"
        except Exception:
            return "No pude calcular la derivada."

    def _integral(self, text: str) -> str:
        try:
            x = symbols("x")
            expr = sympify(text.replace("integral of", ""))
            return f"Integral: {integrate(expr, x)}"
        except Exception:
            return "No pude calcular la integral."