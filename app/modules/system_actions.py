from __future__ import annotations

import difflib
import re
import subprocess
from pathlib import Path


class SystemActionsModule:
    def __init__(self) -> None:
        self.notes_dir = Path.home() / "nova-notes"
        self.notes_dir.mkdir(exist_ok=True)

        self.app_map = {
            "chrome": "Google Chrome",
            "google chrome": "Google Chrome",
            "crono": "Google Chrome",
            "cromo": "Google Chrome",
            "crom": "Google Chrome",
            "safari": "Safari",
            "vscode": "Visual Studio Code",
            "biescoud": "Visual Studio Code",
            "vs code": "Visual Studio Code",
            "visual studio code": "Visual Studio Code",
            "code": "Visual Studio Code",
            "finder": "Finder",
            "terminal": "Terminal",
            "notas": "Notes",
            "notes": "Notes",
            "recordatorios": "Reminders",
            "reminders": "Reminders",
            "calendario": "Calendar",
            "calendar": "Calendar",
        }

    # ----------------------
    # HELPERS
    # ----------------------
    def _normalize(self, text: str) -> str:
        text = text.lower().strip()
        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ü": "u",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_open_target(self, message: str) -> str:
        text = self._normalize(message)

        prefixes = [
            "terra abre ",
            "abre ",
            "abrir ",
            "open ",
        ]
        for prefix in prefixes:
            if text.startswith(prefix):
                return text[len(prefix):].strip()

        return text

    def _resolve_app_name(self, target: str) -> str | None:
        target = self._normalize(target)

        # 1) exact / direct match
        for key, app_name in self.app_map.items():
            if key == target or key in target:
                return app_name

        # 2) fuzzy matching
        candidates = list(self.app_map.keys())
        best = difflib.get_close_matches(target, candidates, n=1, cutoff=0.72)
        if best:
            return self.app_map[best[0]]

        # 3) fallback fonético simple
        phonetic_aliases = {
            "crono": "Google Chrome",
            "crom": "Google Chrome",
            "cromo": "Google Chrome",
            "crohm": "Google Chrome",
            "safary": "Safari",
            "visu al estudio code": "Visual Studio Code",
            "visual estudio code": "Visual Studio Code",
            "v s code": "Visual Studio Code",
            "codee": "Visual Studio Code",
            "recordatorio": "Reminders",
            "nota": "Notes",
        }

        for alias, app_name in phonetic_aliases.items():
            if alias in target:
                return app_name

        return None

    # ----------------------
    # OPEN APPS
    # ----------------------
    def open_app(self, message: str) -> str:
        target = self._extract_open_target(message)
        app_name = self._resolve_app_name(target)

        if not app_name:
            return "No identifiqué la aplicación que quieres abrir."

        subprocess.Popen(["open", "-a", app_name])
        return f"Abrí {app_name}."

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
    # SAVE NOTE IN APPLE NOTES
    # ----------------------
    def save_note(self, message: str) -> str:
        raw = message.strip()

        prefixes = [
            "terra guarda una nota:",
            "terra guarda una nota",
            "guarda una nota:",
            "guarda una nota",
            "crear una nota:",
            "crear una nota",
            "crea una nota:",
            "crea una nota",
            "nota:",
            "nota",
        ]

        normalized = self._normalize(raw)
        content = raw

        for prefix in prefixes:
            if normalized.startswith(self._normalize(prefix)):
                cut = len(prefix)
                content = raw[cut:].strip(" :,-")
                break

        if not content.strip():
            return "No detecté contenido para guardar."

        safe_content = content.replace('"', '\\"')

        script = f'''
        tell application "Notes"
            activate
            tell account "iCloud"
                make new note with properties {{body:"{safe_content}"}}
            end tell
        end tell
        '''

        subprocess.run(["osascript", "-e", script], check=False)
        return "Guardé la nota en Notes."

    # ----------------------
    # SAVE TASK IN REMINDERS
    # ----------------------
    def save_task(self, message: str) -> str:
        raw = message.strip()

        prefixes = [
            "terra crea una tarea:",
            "terra crea una tarea",
            "terra guarda una tarea:",
            "terra guarda una tarea",
            "crea una tarea:",
            "crea una tarea",
            "guarda una tarea:",
            "guarda una tarea",
            "recordatorio:",
            "recordatorio",
            "recuérdame",
            "recuerdame",
            "tarea:",
            "tarea",
        ]

        normalized = self._normalize(raw)
        content = raw

        for prefix in prefixes:
            if normalized.startswith(self._normalize(prefix)):
                cut = len(prefix)
                content = raw[cut:].strip(" :,-")
                break

        if not content.strip():
            return "No detecté la tarea."

        safe_content = content.replace('"', '\\"')

        script = f'''
        tell application "Reminders"
            activate
            tell list "Reminders"
                make new reminder with properties {{name:"{safe_content}"}}
            end tell
        end tell
        '''

        subprocess.run(["osascript", "-e", script], check=False)
        return "Guardé la tarea en Reminders."