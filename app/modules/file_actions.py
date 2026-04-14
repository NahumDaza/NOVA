from __future__ import annotations

import difflib
import re
import subprocess
import unicodedata
from pathlib import Path

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

    def _extract_numbers(self, text: str) -> set[str]:
        return set(re.findall(r"\d+", text))

    def _spoken_filename(self, path: Path) -> str:
        stem = path.stem
        suffix = path.suffix.lower()

        spoken_ext_map = {
            ".pdf": "pe de efe",
            ".png": "pe ene ge",
            ".jpg": "jota pe ge",
            ".jpeg": "jota pe e ge",
            ".doc": "word",
            ".docx": "word",
            ".xls": "excel",
            ".xlsx": "excel",
            ".csv": "si es bi",
            ".txt": "texto",
            ".json": "yeison",
            ".py": "paiton",
        }

        spoken_name = stem.replace("_", " ").replace("-", " ").strip()

        # caso útil para imágenes tipo IMG_2618
        if spoken_name.lower().startswith("img "):
            spoken_name = spoken_name.lower().replace("img ", "imagen ", 1)

        spoken_name = re.sub(r"\s+", " ", spoken_name).strip()
        spoken_ext = spoken_ext_map.get(suffix, suffix.replace(".", "").upper())

        return f"{spoken_name}, {spoken_ext}".strip()

    # -------------------------
    # NORMALIZATION
    # -------------------------
    def _normalize(self, text: str) -> str:
        text = text.strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = text.replace("_", " ")
        text = text.replace("-", " ")
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _compact(self, text: str) -> str:
        return self._normalize(text).replace(" ", "")

    def _clean_search_query(self, message: str) -> str:
        text = self._normalize(message)

        noise_phrases = [
            "terra",
            "busca",
            "buscar",
            "encuentra",
            "abre",
            "abrir",
            "lee",
            "leer",
            "el archivo",
            "archivo",
            "el pdf",
            "pdf",
            "por favor",
            "cierra",
        ]

        for phrase in noise_phrases:
            text = text.replace(phrase, " ")

        text = re.sub(r"\s+", " ", text).strip()
        return text

    # -------------------------
    # FOLDERS
    # -------------------------
    def open_folder(self, message: str) -> str:
        text = self._normalize(message)

        for key, folder_path in self.folder_map.items():
            if self._normalize(key) in text and folder_path.exists():
                subprocess.Popen(["open", str(folder_path)])
                return f"Abrí {folder_path.name}."

        return "No identifiqué la carpeta que quieres abrir."

    # -------------------------
    # FILE SEARCH
    # -------------------------
    def _score_file_match(self, query: str, filename: str) -> float:
        q_norm = self._normalize(query)
        f_norm = self._normalize(filename)

        q_compact = self._compact(query)
        f_compact = self._compact(filename)

        if not q_norm:
            return 0.0

        score = 0.0

        if q_norm == f_norm:
            score += 100

        if q_compact == f_compact:
            score += 95

        if q_norm in f_norm:
            score += 80

        if q_compact in f_compact:
            score += 85

        q_tokens = set(q_norm.split())
        f_tokens = set(f_norm.split())

        common = q_tokens.intersection(f_tokens)
        score += len(common) * 12

        # peso MUY alto para números coincidentes
        q_numbers = self._extract_numbers(q_norm)
        f_numbers = self._extract_numbers(f_norm)

        if q_numbers and f_numbers:
            common_numbers = q_numbers.intersection(f_numbers)
            score += len(common_numbers) * 40

            # penaliza si el query tenía número y el archivo no coincide
            if not common_numbers:
                score -= 25

        score += difflib.SequenceMatcher(None, q_norm, f_norm).ratio() * 50
        score += difflib.SequenceMatcher(None, q_compact, f_compact).ratio() * 50

        return score

    def _find_matches(self, query: str) -> list[Path]:
        scored_matches: list[tuple[float, Path]] = []

        for root in self.search_roots:
            if not root.exists():
                continue

            for path in root.rglob("*"):
                if not path.is_file():
                    continue

                score = self._score_file_match(query, path.name)
                if score >= 45:
                    scored_matches.append((score, path))

        scored_matches.sort(key=lambda x: x[0], reverse=True)
        return [path for _, path in scored_matches[:10]]

    def find_file(self, message: str) -> str:
        query = self._clean_search_query(message)

        if not query:
            return "No detecté el nombre del archivo que quieres buscar."

        matches = self._find_matches(query)
        total_matches = len(matches)
        self.last_found_files = matches[:10]

        if not self.last_found_files:
            return "No encontré archivos con ese nombre."

        first = self.last_found_files[0]
        self.active_file = first

        spoken_first = self._spoken_filename(first)

        if total_matches == 1:
            return f"Encontré el archivo {spoken_first}."

        return f"Encontré {total_matches} archivos. El primero es {spoken_first}."

    def open_found_file(self) -> str:
        if not self.last_found_files:
            return "No tengo archivos encontrados recientemente."

        target = self.last_found_files[0]
        self.active_file = target
        subprocess.Popen(["open", str(target)])
        return f"Abrí {self._spoken_filename(target)}."

    def open_file_by_name(self, message: str) -> str:
        query = self._clean_search_query(message)

        if not query:
            return "No detecté qué archivo quieres abrir."

        matches = self._find_matches(query)

        if not matches:
            return "No encontré un archivo con ese nombre."

        target = matches[0]
        self.last_found_files = matches[:10]
        self.active_file = target
        subprocess.Popen(["open", str(target)])
        return f"Abrí {self._spoken_filename(target)}."

    # -------------------------
    # FILE READING
    # -------------------------
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
        query = self._clean_search_query(message)

        if not query:
            return "No detecté qué archivo quieres leer."

        matches = self._find_matches(query)

        if not matches:
            return "No encontré un archivo con ese nombre."

        target = matches[0]
        self.last_found_files = matches[:10]
        self.active_file = target
        return self._read_file(target)

    def get_active_file_name(self) -> str:
        if not self.active_file:
            return "No tengo un archivo activo en este momento."
        return f"El archivo activo es {self._spoken_filename(self.active_file)}."

    # -------------------------
    # LOW-LEVEL READERS
    # -------------------------
    def _read_file(self, path: Path) -> str:
        suffix = path.suffix.lower()

        try:
            if suffix == ".pdf":
                return self._read_pdf(path)

            if suffix in self.readable_text_extensions:
                content = path.read_text(encoding="utf-8", errors="ignore").strip()
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