from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout

from app.ui.icons import icon_pixmap, readable_on


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "0", subtitle: str = "", icon: str = "dashboard", accent: str = "#2563EB", parent=None) -> None:
        super().__init__(parent)
        self.setProperty("card", True)
        self.setMinimumHeight(112)
        self.setFixedHeight(112)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.accent = accent
        self.icon_name = icon
        root = QHBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(15)

        self.icon_label = QLabel(icon)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(50, 50)
        self.icon_label.setPixmap(icon_pixmap(icon, readable_on(accent), 25))
        self.icon_label.setStyleSheet(f"background:{accent}; border-radius:14px;")

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)
        self.title_label = QLabel(title)
        self.title_label.setProperty("muted", True)
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size:24px; font-weight:850;")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setProperty("muted", True)
        self.subtitle_label.setWordWrap(False)
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.value_label)
        text_layout.addWidget(self.subtitle_label)

        root.addWidget(self.icon_label)
        root.addLayout(text_layout, 1)

    def set_value(self, value: str, subtitle: str = "") -> None:
        self.value_label.setText(value)
        self.subtitle_label.setText(subtitle)

    def set_icon(self, icon: str, accent: str | None = None) -> None:
        self.icon_name = icon
        if accent:
            self.accent = accent
            self.icon_label.setStyleSheet(f"background:{self.accent}; border-radius:14px;")
        self.icon_label.setPixmap(icon_pixmap(icon, readable_on(self.accent), 25))
