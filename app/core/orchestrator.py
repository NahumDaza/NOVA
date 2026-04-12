from __future__ import annotations

import re

from app.core.router import IntentRouter
from app.core.terra_persona import TerraPersona
from app.core.terra_state import TerraStateStore
from app.modules.comms import CommsModule
from app.modules.logic import LogicModule
from app.modules.strategy import StrategyModule
from app.modules.work import WorkModule
from app.services.english_coach import EnglishCoach
from app.memory.history import ConversationMemory
from app.services.llm_service import LLMService
from app.core.postprocessor import ResponsePostProcessor
from app.modules.text_tools import TextToolsModule
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
        self.persona = TerraPersona()
        self.terra_state = TerraStateStore()
        self.text_tools = TextToolsModule()

    def _strip_leading_greeting(self, text: str) -> str:
        cleaned = text.strip()

        patterns = [
            r"^\s*[¡!]*\s*hola\s*,?\s*nahum\s*[!,.:\-\s]*",
            r"^\s*[¡!]*\s*hola\s*,?\s*jefe\s*[!,.:\-\s]*",
            r"^\s*[¡!]*\s*hola\s*,?\s*terra\s*[!,.:\-\s]*",
            r"^\s*[¡!]*\s*hola\s*[!,.:\-\s]*",
            r"^\s*buenos\s+d[ií]as\s*,?\s*nahum\s*[!,.:\-\s]*",
            r"^\s*buenas\s+tardes\s*,?\s*nahum\s*[!,.:\-\s]*",
            r"^\s*buenas\s+noches\s*,?\s*nahum\s*[!,.:\-\s]*",
            r"^\s*bienvenido\s+de\s+nuevo\s*,?\s*nahum\s*[!,.:\-\s]*",
            r"^\s*bienvenido\s+de\s+nuevo\s*,?\s*jefe\s*[!,.:\-\s]*",
            r"^\s*aqu[ií]\s+estoy\s*,?\s*jefe\s*[!,.:\-\s]*",
            r"^\s*todo\s+en\s+orden\s*,?\s*(nahum|jefe)?\s*[!,.:\-\s]*",
        ]

        changed = True
        while changed:
            changed = False
            for pattern in patterns:
                new_cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
                if new_cleaned != cleaned:
                    cleaned = new_cleaned
                    changed = True

        return cleaned
    
    def _is_simple_greeting_to_terra(self, message: str) -> bool:
        text = message.lower()

        greeting_words = [
            "hola terra",
            "hola, terra",
            "buen día terra",
            "buen dia terra",
            "buenas tardes terra",
            "buenas noches terra",
            "qué tal",
            "que tal",
            "cómo vas",
            "como vas",
            "cómo estás",
            "como estas",
        ]

        mentions_terra = "terra" in text
        short_message = len(text.split()) <= 8

        return mentions_terra and any(word in text for word in greeting_words) and short_message
    
    def _terra_greeting_response(self, conversation_id: str) -> tuple[str, str]:
        state = self.terra_state.get(conversation_id)
        greeting = self.persona.greeting_for_context(state)
        state.last_greeting = greeting

        response_options = [
            "Estoy bien. ¿Cómo vas tú?",
            "Todo en orden. ¿Cómo va tu día?",
            "Aquí estoy. ¿En qué te ayudo?",
            "Todo bien por aquí. ¿Qué necesitas?",
        ]

        import random
        spoken = f"{greeting} {random.choice(response_options)}"
        visual = spoken

        return visual, spoken

    def _apply_terra_style(
        self,
        intent: str,
        response: str,
        conversation_id: str,
    ) -> str:
        state = self.terra_state.get(conversation_id)
        base_response = self._strip_leading_greeting(response)

        if intent == "draft_message":
            confirmation = self.persona.confirmation(state)
            followup = self.persona.followup(state)

            state.last_confirmation = confirmation
            state.last_followup = followup

            if followup:
                return f"{confirmation} Preparé el correo para tu profesor. {followup}".strip()
            return f"{confirmation} Preparé el correo para tu profesor.".strip()

        if intent == "refine_previous_output":
            confirmation = self.persona.confirmation(state)
            followup = self.persona.followup(state)

            state.last_confirmation = confirmation
            state.last_followup = followup

            if followup:
                return f"{confirmation} Hice el ajuste. {followup}".strip()
            return f"{confirmation} Hice el ajuste.".strip()

        if intent == "general_chat":
            greeting = self.persona.greeting_for_context(state)
            state.last_greeting = greeting

            if base_response:
                return f"{greeting} {base_response}".strip()
            return greeting
        
        if intent == "summarize_text":
            return "Listo. Ya preparé el resumen."

        if intent == "translate_text":
            return "Hecho. Ya dejé la traducción lista."

        if intent == "rewrite_text":
            return "En orden. Ya ajusté el texto."

        return base_response or response

    def handle(
        self,
        message: str,
        language: str = "auto",
        conversation_id: str = "default",
        use_memory: bool = True,
    ) -> dict:
        correction = self.english_coach.maybe_correct(message, language=language)
        intent = self.router.detect_intent(message)

        if self._is_simple_greeting_to_terra(message):
            response, spoken_response = self._terra_greeting_response(conversation_id)

            if use_memory:
                self.memory.add_user_message(conversation_id, message)
                self.memory.add_assistant_message(conversation_id, response)

            self.terra_state.touch(conversation_id)

            return {
                "intent": "general_chat",
                "response": response,
                "spoken_response": spoken_response,
                "correction": correction,
                "approval_required": False,
                "conversation_id": conversation_id,
            }

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

        elif intent == "summarize_text":
            response = self.text_tools.summarize(message=message, language=language)

        elif intent == "translate_text":
            response = self.text_tools.translate(message=message, language=language)

        elif intent == "rewrite_text":
            response = self.text_tools.rewrite(message=message, language=language)

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
            conversation_id=conversation_id,
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

        self.terra_state.touch(conversation_id)

        return {
            "intent": intent,
            "response": response,
            "spoken_response": spoken_response,
            "correction": correction,
            "approval_required": approval_required,
            "conversation_id": conversation_id,
        }