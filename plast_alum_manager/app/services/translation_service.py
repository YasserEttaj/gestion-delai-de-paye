from __future__ import annotations

import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from config import TRANSLATION_DIR


SUPPORTED_LANGUAGES = {"fr", "en"}
DEFAULT_LANGUAGE = "fr"


class TranslationService:
    def __init__(self, language: str = "fr") -> None:
        self.language = self._normalize(language)
        self.messages = self._load(self.language)

    @staticmethod
    def _normalize(language: str | None) -> str:
        return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

    def _load(self, language: str) -> dict[str, str]:
        language = self._normalize(language)
        path = TRANSLATION_DIR / f"{language}.json"
        if not path.exists():
            path = TRANSLATION_DIR / "fr.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def set_language(self, language: str) -> None:
        self.language = self._normalize(language)
        self.messages = self._load(language)
        app = QApplication.instance()
        if app:
            app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def tr(self, key: str, default: str | None = None) -> str:
        return self.messages.get(key, default or key)
