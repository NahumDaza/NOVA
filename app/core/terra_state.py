from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class TerraConversationState:
    last_greeting: Optional[str] = None
    last_confirmation: Optional[str] = None
    last_followup: Optional[str] = None
    last_interaction_at: Optional[datetime] = None


class TerraStateStore:
    def __init__(self) -> None:
        self._store: dict[str, TerraConversationState] = {}

    def get(self, conversation_id: str) -> TerraConversationState:
        if conversation_id not in self._store:
            self._store[conversation_id] = TerraConversationState()
        return self._store[conversation_id]

    def touch(self, conversation_id: str) -> None:
        state = self.get(conversation_id)
        state.last_interaction_at = datetime.now()

    def seconds_since_last_interaction(self, conversation_id: str) -> Optional[float]:
        state = self.get(conversation_id)
        if not state.last_interaction_at:
            return None
        return (datetime.now() - state.last_interaction_at).total_seconds()