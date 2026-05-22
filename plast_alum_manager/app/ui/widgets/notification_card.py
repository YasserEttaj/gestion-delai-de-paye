from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class NotificationCard(QFrame):
    COLORS = {
        "normal": "#22C55E",
        "attention": "#F59E0B",
        "urgent": "#EF4444",
        "critical": "#7F1D1D",
        "info": "#2563EB",
    }

    def __init__(self, title: str, message: str, level: str = "info", parent=None) -> None:
        super().__init__(parent)
        self.setProperty("card", True)
        color = self.COLORS.get(level, "#2563EB")
        self.setStyleSheet(f"border-left: 4px solid {color};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight:800;")
        self.message_label = QLabel(message)
        self.message_label.setProperty("muted", True)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.title_label)
        layout.addWidget(self.message_label)
