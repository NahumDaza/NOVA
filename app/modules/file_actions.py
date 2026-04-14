from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from pypdf import PdfReader


class FileActionsModule:
    def __init__(self) -> None:
        self.last_found_files: list[Path] = []
        self.active_file: Path | None = None

        self.folder_map = {
            "descargas": Path.home() / "Downloads",
            "downloads": Path.home() / "Downloads",
            "documentos": Path.home() / "Documents",
            "documents": Path.home() / "Documents",
            "escritorio": Path.home() / "Desktop",
            "desktop": Path.home() / "Desktop",
            "proyectos": Path.home() / "NOVA",
            "project": Path.home() / "NOVA",
            "projects": Path.home() / "NOVA",
            "carpeta de proyectos": Path.home() / "NOVA",
            "mi carpeta de proyectos": Path.home() / "NOVA",
            "nova": Path.home() / "NOVA",
        }

        self.search_roots = [
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path.home() / "Downloads",
            Path.home() / "NOVA",
        ]

        self.readable_text_extensions = {
            ".txt", ".md", ".py", ".json", ".csv", ".xml", ".yaml", ".yml", ".log"
        }

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
            .replace("el pdf", "")
            .replace("pdf", "")
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
        self.active_file = first
        return f"Encontré {len(self.last_found_files)} archivo(s). El primero es {first.name}."

    def open_found_file(self) -> str:
        if not self.last_found_files:
            return "No tengo archivos encontrados recientemente."

        target = self.last_found_files[0]
        self.active_file = target
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
        self.active_file = target
        subprocess.Popen(["open", str(target)])
        return f"Abrí {target.name}."

    def read_active_file(self) -> str:
        if not self.active_file:
            return "No tengo un archivo activo para leer."

        return self._read_file(self.active_file)

    def read_last_found_file(self) -> str:
        if not self.last_found_files:
            return "No tengo archivos encontrados recientemente."

        self.active_file = self.last_found_files[0]
        return self._read_file(self.active_file)

    def read_file_by_name(self, message: str) -> str:
        text = message.lower()
        query = (
            text.replace("terra", "")
            .replace("lee", "")
            .replace("leer", "")
            .replace("el archivo", "")
            .replace("archivo", "")
            .replace("el pdf", "")
            .replace("pdf", "")
            .strip(" :,.")
        )

        if not query:
            return "No detecté qué archivo quieres leer."

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
        self.active_file = target
        return self._read_file(target)

    def get_active_file_name(self) -> str:
        if not self.active_file:
            return "No tengo un archivo activo en este momento."
        return f"El archivo activo es {self.active_file.name}."

    def _read_file(self, path: Path) -> str:
        suffix = path.suffix.lower()

        try:
            if suffix == ".pdf":
                return self._read_pdf(path)

            if suffix in self.readable_text_extensions:
                content = path.read_text(encoding="utf-8", errors="ignore")
                content = content.strip()
                if not content:
                    return f"El archivo {path.name} está vacío."
                return self._truncate_content(path.name, content)

            return f"Puedo abrir {path.name}, pero todavía no tengo lectura implementada para archivos {suffix}."
        except Exception as exc:
            return f"No pude leer {path.name}. Error: {exc}"

    def _read_pdf(self, path: Path) -> str:
        reader = PdfReader(str(path))
        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text.strip())

        full_text = "\n".join(pages).strip()

        if not full_text:
            return f"No pude extraer texto útil de {path.name}."

        return self._truncate_content(path.name, full_text)

    def _truncate_content(self, filename: str, content: str, max_chars: int = 5000) -> str:
        cleaned = " ".join(content.split())
        if len(cleaned) <= max_chars:
            return f"Contenido de {filename}: {cleaned}"
        return f"Contenido de {filename}: {cleaned[:max_chars].rsplit(' ', 1)[0]}..."