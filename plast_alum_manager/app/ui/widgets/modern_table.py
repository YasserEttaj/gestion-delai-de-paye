from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem

from app.ui.icons import COLOR_WHITE, icon_pixmap


class ModernTable(QTableWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSortingEnabled(False)

    def set_headers(self, headers: list[str]) -> None:
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    def set_text_item(self, row: int, column: int, text: str | int | float | None, align_right: bool = False) -> None:
        item = QTableWidgetItem("" if text is None else str(text))
        if align_right:
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setItem(row, column, item)

    def badge(self, text: str, color: str, icon_name: str | None = None) -> QFrame:
        badge = QFrame()
        badge.setStyleSheet(f"background:{color}; color:white; border-radius:10px;")
        layout = QHBoxLayout(badge)
        layout.setContentsMargins(8, 3, 8, 3)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icon_name:
            icon = QLabel()
            icon.setFixedSize(14, 14)
            icon.setPixmap(icon_pixmap(icon_name, COLOR_WHITE, 14))
            layout.addWidget(icon)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color:white; font-weight:700;")
        layout.addWidget(label)
        return badge

    def empty(self, message: str, columns: int) -> None:
        self.show_empty(message, columns)

    def show_empty(self, message: str, columns: int | None = None) -> None:
        columns = columns or self.columnCount()
        self.setRowCount(1)
        if self.columnCount() != columns:
            self.setColumnCount(columns)
        self.setSpan(0, 0, 1, columns)
        item = QTableWidgetItem(message)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.setItem(0, 0, item)
        self.setRowHeight(0, 72)
