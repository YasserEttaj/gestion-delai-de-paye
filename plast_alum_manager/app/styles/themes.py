from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QApplication


STYLE_DIR = Path(__file__).resolve().parent


def apply_theme(app: QApplication, theme: str) -> None:
    theme = "light" if theme == "light" else "dark"
    qss_path = STYLE_DIR / f"{theme}.qss"
    app.setStyle("Fusion")
    app.setProperty("theme", theme)
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
