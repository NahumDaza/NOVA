from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


class FileActionsModule:
    def __init__(self) -> None:
        self.last_found_files: list[Path] = []

        self.folder_map = {
            "descargas": Path.home() / "Downloads",
            "downloads": Path.home() / "Downloads",
            "documentos": Path.home() / "Documents",
            "documents": Path.home() / "Documents",
            "escritorio": Path.home() / "Desktop",
            "desktop": Path.home() / "Desktop",
            "proyectos": Path.home() / "Projects",
            "projects": Path.home() / "Projects",
            "carpeta de proyectos": Path.home() / "Projects",
            "mi carpeta de proyectos": Path.home() / "Projects",
            "nueva": Path.home() / "NOVA",
            "nova": Path.home() / "NOVA",
        }

        self.search_roots = [
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path.home() / "Downloads",
            Path.home() / "NOVA",
        ]

    def open_folder(self, message: str) -> str:
        text = message.lower()

        for key, folder_path in self.folder_map.items():
            if key in text and folder_path.exists():
                subprocess.Popen(["open", str(folder_path)])
                return f"Abrí {folder_path.name}."

        return "No identifiqué la carpeta que quieres abrir."

    def find_file(self, message: str) -> str:
        text = message.lower()
        query = (
            text.replace("terra", "")
            .replace("busca", "")
            .replace("buscar", "")
            .replace("encuentra", "")
            .replace("el archivo", "")
            .replace("archivo", "")
            .strip(" :,.")
        )

        if not query:
            return "No detecté el nombre del archivo que quieres buscar."

        matches: list[Path] = []

        for root in self.search_roots:
            if not root.exists():
                continue

            for path in root.rglob("*"):
                if path.is_file() and query in path.name.lower():
                    matches.append(path)

        self.last_found_files = matches[:10]

        if not self.last_found_files:
            return "No encontré archivos con ese nombre."

        first = self.last_found_files[0]
        return f"Encontré {len(self.last_found_files)} archivo(s). El primero es {first.name}."

    def open_found_file(self) -> str:
        if not self.last_found_files:
            return "No tengo archivos encontrados recientemente."

        target = self.last_found_files[0]
        subprocess.Popen(["open", str(target)])
        return f"Abrí {target.name}."

    def open_file_by_name(self, message: str) -> str:
        text = message.lower()
        query = (
            text.replace("terra", "")
            .replace("abre", "")
            .replace("abrir", "")
            .replace("el archivo", "")
            .replace("archivo", "")
            .strip(" :,.")
        )

        if not query:
            return "No detecté qué archivo quieres abrir."

        matches: list[Path] = []

        for root in self.search_roots:
            if not root.exists():
                continue

            for path in root.rglob("*"):
                if path.is_file() and query in path.name.lower():
                    matches.append(path)

        if not matches:
            return "No encontré un archivo con ese nombre."

        target = matches[0]
        self.last_found_files = matches[:10]
        subprocess.Popen(["open", str(target)])
        return f"Abrí {target.name}."