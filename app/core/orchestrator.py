from app.core.router import IntentRouter
from app.modules.comms import CommsModule
from app.modules.logic import LogicModule
from app.modules.strategy import StrategyModule
from app.modules.work import WorkModule
from app.services.english_coach import EnglishCoach
from app.memory.history import ConversationMemory
from app.services.llm_service import LLMService


class Orchestrator:
    def __init__(self) -> None:
        self.router = IntentRouter()
        self.work = WorkModule()
        self.comms = CommsModule()
        self.logic = LogicModule()
        self.strategy = StrategyModule()
        self.english_coach = EnglishCoach()
        self.memory = ConversationMemory()
        self.llm = LLMService()

    def handle(
        self,
        message: str,
        language: str = "auto",
        conversation_id: str = "default",
        use_memory: bool = True,
    ) -> dict:
        correction = self.english_coach.maybe_correct(message, language=language)
        intent = self.router.detect_intent(message)

        if use_memory:
            self.memory.add_user_message(conversation_id, message)
            recent_history = self.memory.get_recent(conversation_id)
        else:
            recent_history = []

        if intent == "organize_day":
            response = self.work.organize_day(message)
        elif intent == "draft_message":
            response = self.comms.draft_message(message)
        elif intent in {"calculate_math", "solve_physics", "solve_chemistry"}:
            response = self.logic.solve(message, intent=intent)
        elif intent == "think_process":
            response = self.strategy.think_process(message)
        elif intent == "improve_english":
            response = correction or "No veo un error importante en tu inglés. Envíame la frase y te la corrijo o mejoro."
        else:
            response = self.llm.generate(
                system_prompt="Eres NOVA. Tu idioma principal es español.",
                user_message=message,
                history=recent_history,
            )

        if use_memory:
            self.memory.add_assistant_message(conversation_id, response)

        return {
            "intent": intent,
            "response": response,
            "correction": correction,
            "approval_required": intent == "draft_message",
            "conversation_id": conversation_id,
        }