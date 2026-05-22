from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QWidget


class SearchBar(QWidget):
    def __init__(self, placeholder: str = "Recherche", parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.input = QLineEdit()
        self.input.setClearButtonEnabled(True)
        self.input.setPlaceholderText(placeholder)
        layout.addWidget(self.input)

    def text(self) -> str:
        return self.input.text()

    def set_placeholder(self, text: str) -> None:
        self.input.setPlaceholderText(text)
