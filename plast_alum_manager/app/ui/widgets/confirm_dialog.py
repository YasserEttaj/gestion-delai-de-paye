from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox, QWidget


class ConfirmDialog:
    @staticmethod
    def ask(parent: QWidget, title: str, message: str) -> bool:
        dialog = QMessageBox(parent)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        return dialog.exec() == QMessageBox.StandardButton.Yes

    @staticmethod
    def info(parent: QWidget, title: str, message: str) -> None:
        QMessageBox.information(parent, title, message)

    @staticmethod
    def error(parent: QWidget, title: str, message: str) -> None:
        QMessageBox.critical(parent, title, message)
