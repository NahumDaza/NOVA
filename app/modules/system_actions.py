from __future__ import annotations

import subprocess
from pathlib import Path
from datetime import datetime


class SystemActionsModule:
    def __init__(self) -> None:
        self.notes_dir = Path.home() / "nova-notes"
        self.notes_dir.mkdir(exist_ok=True)

    # ----------------------
    # OPEN APPS
    # ----------------------
    def open_app(self, message: str) -> str:
        text = message.lower()

        app_map = {
            "chrome": "Google Chrome",
            "google chrome": "Google Chrome",
            "safari": "Safari",
            "vscode": "Visual Studio Code",
            "code": "Visual Studio Code",
            "finder": "Finder",
            "terminal": "Terminal",
        }

        for key, app_name in app_map.items():
            if key in text:
                subprocess.Popen(["open", "-a", app_name])
                return f"Abrí {app_name}."

        return "No identifiqué la aplicación que quieres abrir."

    # ----------------------
    # COPY TO CLIPBOARD
    # ----------------------
    def copy_to_clipboard(self, text: str) -> str:
        process = subprocess.Popen(
            ["pbcopy"],
            stdin=subprocess.PIPE,
            text=True,
        )
        process.communicate(text)
        return "Lo copié al portapapeles."

    # ----------------------
    # SAVE NOTE
    # ----------------------
    def save_note(self, message: str) -> str:
        content = message.replace("nota", "").replace("guardar nota", "").strip()

        if not content:
            return "No detecté contenido para guardar."

        filename = datetime.now().strftime("note_%Y%m%d_%H%M%S.txt")
        file_path = self.notes_dir / filename

        file_path.write_text(content, encoding="utf-8")

        return f"Guardé la nota."

    # ----------------------
    # SAVE TASK
    # ----------------------
    def save_task(self, message: str) -> str:
        content = message.replace("tarea", "").replace("recordatorio", "").strip()

        if not content:
            return "No detecté la tarea."

        file_path = self.notes_dir / "tasks.txt"

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"- {content}\n")

        return "Guardé la tarea."