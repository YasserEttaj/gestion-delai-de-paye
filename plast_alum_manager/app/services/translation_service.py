from __future__ import annotations

import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from config import TRANSLATION_DIR


class TranslationService:
    def __init__(self, language: str = "fr") -> None:
        self.language = language
        self.messages = self._load(language)

    def _load(self, language: str) -> dict[str, str]:
        path = TRANSLATION_DIR / f"{language}.json"
        if not path.exists():
            path = TRANSLATION_DIR / "fr.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def set_language(self, language: str) -> None:
        self.language = language
        self.messages = self._load(language)
        app = QApplication.instance()
        if app:
            direction = Qt.LayoutDirection.RightToLeft if language == "ar" else Qt.LayoutDirection.LeftToRight
            app.setLayoutDirection(direction)

    def tr(self, key: str, default: str | None = None) -> str:
        return self.messages.get(key, default or key)
