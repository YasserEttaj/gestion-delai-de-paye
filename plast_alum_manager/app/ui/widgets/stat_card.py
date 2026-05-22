from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout


class StatCard(QFrame):
    def __init__(self, title: str, value: str = "0", subtitle: str = "", icon: str = "■", accent: str = "#2563EB", parent=None) -> None:
        super().__init__(parent)
        self.setProperty("card", True)
        self.setMinimumHeight(100)
        self.setFixedHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.accent = accent
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(14)

        self.icon_label = QLabel(icon)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(42, 42)
        self.icon_label.setStyleSheet(f"background:{accent}; color:white; border-radius:12px; font-size:20px;")

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        self.title_label = QLabel(title)
        self.title_label.setProperty("muted", True)
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size:23px; font-weight:800;")
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
