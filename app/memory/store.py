from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager

from dotenv import load_dotenv

load_dotenv()


class MemoryStore:
    def __init__(self) -> None:
        self.db_path = os.getenv("NOVA_DB_PATH", "data/nova.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self.connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_artifacts (
                    conversation_id TEXT PRIMARY KEY,
                    artifact_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO conversation_messages (conversation_id, role, content)
                VALUES (?, ?, ?)
                """,
                (conversation_id, role, content),
            )

    def get_recent_messages(self, conversation_id: str, limit: int = 6) -> list[dict[str, str]]:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                SELECT role, content
                FROM conversation_messages
                WHERE conversation_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (conversation_id, limit),
            )
            rows = cursor.fetchall()

        rows.reverse()
        return [{"role": role, "content": content} for role, content in rows]

    def save_artifact(self, conversation_id: str, artifact_type: str, content: str) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO conversation_artifacts (conversation_id, artifact_type, content, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(conversation_id)
                DO UPDATE SET
                    artifact_type = excluded.artifact_type,
                    content = excluded.content,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (conversation_id, artifact_type, content),
            )

    def get_artifact(self, conversation_id: str) -> dict[str, str] | None:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                SELECT artifact_type, content
                FROM conversation_artifacts
                WHERE conversation_id = ?
                """,
                (conversation_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        artifact_type, content = row
        return {
            "type": artifact_type,
            "content": content,
        }

    def clear_conversation(self, conversation_id: str) -> None:
        with self.connection() as conn:
            conn.execute(
                "DELETE FROM conversation_messages WHERE conversation_id = ?",
                (conversation_id,),
            )
            conn.execute(
                "DELETE FROM conversation_artifacts WHERE conversation_id = ?",
                (conversation_id,),
            )