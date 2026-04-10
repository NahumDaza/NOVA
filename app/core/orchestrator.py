from app.core.router import IntentRouter
from app.modules.comms import CommsModule
from app.modules.logic import LogicModule
from app.modules.strategy import StrategyModule
from app.modules.work import WorkModule
from app.services.english_coach import EnglishCoach


class Orchestrator:
    def __init__(self) -> None:
        self.router = IntentRouter()
        self.work = WorkModule()
        self.comms = CommsModule()
        self.logic = LogicModule()
        self.strategy = StrategyModule()
        self.english_coach = EnglishCoach()

    def handle(self, message: str, language: str = "auto") -> dict:
        correction = self.english_coach.maybe_correct(message, language=language)
        intent = self.router.detect_intent(message)

        if intent == "organize_day":
            response = self.work.organize_day(message)
            return self._result(intent, response, correction, approval_required=False)

        if intent == "draft_message":
            response = self.comms.draft_message(message)
            return self._result(intent, response, correction, approval_required=True)

        if intent in {"calculate_math", "solve_physics", "solve_chemistry"}:
            response = self.logic.solve(message, intent=intent)
            return self._result(intent, response, correction, approval_required=False)

        if intent == "think_process":
            response = self.strategy.think_process(message)
            return self._result(intent, response, correction, approval_required=False)

        if intent == "improve_english":
            response = correction or "I don’t see a major issue in your English. Send me the sentence and I’ll refine it."
            return self._result(intent, response, correction, approval_required=False)

        response = self.work.general_assist(message)
        return self._result(intent, response, correction, approval_required=False)

    def _result(self, intent: str, response: str, correction: str | None, approval_required: bool) -> dict:
        return {
            "intent": intent,
            "response": response,
            "correction": correction,
            "approval_required": approval_required,
        }