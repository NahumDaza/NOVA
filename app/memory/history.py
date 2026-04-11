from __future__ import annotations

from app.memory.store import MemoryStore


class ConversationMemory:
    def __init__(self) -> None:
        self.store = MemoryStore()

    def add_user_message(self, conversation_id: str, message: str) -> None:
        self.store.add_message(conversation_id, "user", message)

    def add_assistant_message(self, conversation_id: str, message: str) -> None:
        self.store.add_message(conversation_id, "assistant", message)

    def get_recent(self, conversation_id: str, limit: int = 6) -> list[dict[str, str]]:
        return self.store.get_recent_messages(conversation_id, limit=limit)

    def clear(self, conversation_id: str) -> None:
        self.store.clear_conversation(conversation_id)

    def save_last_artifact(self, conversation_id: str, artifact_type: str, content: str) -> None:
        self.store.save_artifact(conversation_id, artifact_type, content)

    def get_last_artifact(self, conversation_id: str) -> dict[str, str] | None:
        return self.store.get_artifact(conversation_id)