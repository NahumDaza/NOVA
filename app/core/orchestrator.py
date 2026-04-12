from app.core.router import IntentRouter
from app.modules.comms import CommsModule
from app.modules.logic import LogicModule
from app.modules.strategy import StrategyModule
from app.modules.work import WorkModule
from app.services.english_coach import EnglishCoach
from app.memory.history import ConversationMemory
from app.services.llm_service import LLMService
from app.core.postprocessor import ResponsePostProcessor
from app.prompts.system_prompt import NOVA_SYSTEM_PROMPT


class Orchestrator:
    def __init__(self) -> None:
        self.router = IntentRouter()
        self.work = WorkModule()
        self.comms = CommsModule()
        self.logic = LogicModule()
        self.strategy = StrategyModule()
        self.english_coach = EnglishCoach()
        self.memory = ConversationMemory()
        self.postprocessor = ResponsePostProcessor()
        self.llm = LLMService()

    def _apply_terra_style(self, intent: str, response: str) -> str:
        import random

        greetings = [
            "Hola, Nahum.",
            "Aquí estoy, jefe.",
            "Todo en orden.",
        ]

        confirmations = [
            "Hecho.",
            "Ya quedó listo.",
            "Listo.",
            "En orden.",
        ]

        followups = [
            "Lo ajusto si quieres.",
            "Puedo afinarlo.",
            "Lo adapto enseguida.",
            "",
        ]

        if intent == "draft_message":
            prefix = random.choice(confirmations)
            suffix = random.choice(followups)
            return f"{prefix} Preparé el correo para tu profesor. {suffix}".strip()

        if intent == "refine_previous_output":
            prefix = random.choice(confirmations)
            suffix = random.choice(followups)
            return f"{prefix} Hice el ajuste. {suffix}".strip()

        if intent == "general_chat":
            prefix = random.choice(greetings)
            return f"{prefix} {response}".strip()

        return response

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
            last_artifact = self.memory.get_last_artifact(conversation_id)
        else:
            recent_history = []
            last_artifact = None

        approval_required = False

        if intent == "organize_day":
            response = self.work.organize_day(message)

        elif intent == "draft_message":
            response = self.comms.draft_message(message=message, language=language)
            approval_required = True

        elif intent == "refine_previous_output":
            if last_artifact and last_artifact.get("content"):
                response = self.llm.refine_text(
                    original_text=last_artifact["content"],
                    instruction=message,
                    language=language,
                )
                approval_required = last_artifact.get("type") == "draft_message"
            else:
                response = (
                    "No tengo un contenido previo claro para refinar en esta conversación. "
                    "Primero dame el borrador, texto o contenido base."
                )

        elif intent in {"calculate_math", "solve_physics", "solve_chemistry"}:
            response = self.logic.solve(message, intent=intent)

        elif intent == "think_process":
            response = self.strategy.think_process(message)

        elif intent == "improve_english":
            response = correction or (
                "No veo un error importante en tu inglés. "
                "Envíame la frase y te la corrijo o mejoro."
            )

        else:
            response = self.llm.generate(
                system_prompt=NOVA_SYSTEM_PROMPT,
                user_message=message,
                history=recent_history,
            )

        response = self.postprocessor.clean(
            intent=intent,
            response=response,
            language=language,
        )

        spoken_response = self._apply_terra_style(
            intent=intent,
            response=response,
        )

        if use_memory:
            self.memory.add_assistant_message(conversation_id, response)

            if intent == "draft_message":
                self.memory.save_last_artifact(conversation_id, "draft_message", response)

            elif intent == "refine_previous_output" and last_artifact and last_artifact.get("content"):
                self.memory.save_last_artifact(
                    conversation_id,
                    last_artifact.get("type", "text"),
                    response,
                )

        return {
            "intent": intent,
            "response": response,
            "spoken_response": spoken_response,
            "correction": correction,
            "approval_required": approval_required,
            "conversation_id": conversation_id,
        }