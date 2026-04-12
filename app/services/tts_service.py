from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path


class XTTSService:
    def __init__(self) -> None:
        self.python_bin = "/Users/macuser/nova-xtts-venv-arm/bin/python"
        self.script_path = "/Users/macuser/NOVA/scripts/xtts_generate.py"
        self.audio_dir = Path("/Users/macuser/nova-audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text: str) -> str:
        spoken_text = self._prepare_text_for_tts(text)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=self.audio_dir) as tmp:
            output_path = tmp.name

        subprocess.run(
            [self.python_bin, self.script_path, spoken_text, output_path],
            capture_output=True,
            text=True,
            check=True,
        )

        return output_path

    def _prepare_text_for_tts(self, text: str) -> str:
        prepared = text.strip()

        pronunciation_replacements = {
            "Nahum Daza": "Naúm Daza",
            "Nahum": "Naúm",
            "NOVA": "Nóva",
        }

        for old, new in pronunciation_replacements.items():
            prepared = prepared.replace(old, new)

        # quitar prefacios innecesarios para que suene más natural
        prefixes = [
            "Claro, aquí tienes un borrador del correo que puedes enviar a tu profesor:",
            "Aquí tienes un borrador del correo:",
            "Claro, aquí tienes el correo:",
        ]
        for prefix in prefixes:
            prepared = prepared.replace(prefix, "").strip()

        # simplificar puntuación que puede causar pausas raras
        prepared = prepared.replace(":", ".")
        prepared = prepared.replace(";", ".")
        prepared = prepared.replace("...", ".")
        prepared = prepared.replace("\n", " ")

        # colapsar espacios
        prepared = re.sub(r"\s+", " ", prepared).strip()

        return prepared