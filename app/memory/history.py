from collections import defaultdict
from typing import Any


class ConversationMemory:
    def __init__(self) -> None:
        self.history_store: dict[str, list[dict[str, str]]] = defaultdict(list)
        self.artifact_store: dict[str, dict[str, Any]] = defaultdict(dict)

    def add_user_message(self, conversation_id: str, message: str) -> None:
        self.history_store[conversation_id].append({"role": "user", "content": message})

    def add_assistant_message(self, conversation_id: str, message: str) -> None:
        self.history_store[conversation_id].append({"role": "assistant", "content": message})

    def get_recent(self, conversation_id: str, limit: int = 6) -> list[dict[str, str]]:
        return self.history_store[conversation_id][-limit:]

    def clear(self, conversation_id: str) -> None:
        self.history_store[conversation_id] = []
        self.artifact_store[conversation_id] = {}

    def save_last_artifact(self, conversation_id: str, artifact_type: str, content: str) -> None:
        self.artifact_store[conversation_id] = {
            "type": artifact_type,
            "content": content,
        }

    def get_last_artifact(self, conversation_id: str) -> dict[str, Any] | None:
        artifact = self.artifact_store.get(conversation_id)
        return artifact if artifact else None