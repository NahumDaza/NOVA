from collections import defaultdict


class ConversationMemory:
    def __init__(self) -> None:
        self.store: dict[str, list[dict[str, str]]] = defaultdict(list)

    def add_user_message(self, conversation_id: str, message: str) -> None:
        self.store[conversation_id].append({"role": "user", "content": message})

    def add_assistant_message(self, conversation_id: str, message: str) -> None:
        self.store[conversation_id].append({"role": "assistant", "content": message})

    def get_recent(self, conversation_id: str, limit: int = 6) -> list[dict[str, str]]:
        return self.store[conversation_id][-limit:]

    def clear(self, conversation_id: str) -> None:
        self.store[conversation_id] = []