from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox, QWidget


class ToastNotification:
    @staticmethod
    def success(parent: QWidget, message: str) -> None:
        QMessageBox.information(parent, "Succès", message)

    @staticmethod
    def error(parent: QWidget, message: str) -> None:
        QMessageBox.critical(parent, "Erreur", message)

    @staticmethod
    def warning(parent: QWidget, message: str) -> None:
        QMessageBox.warning(parent, "Attention", message)

    @staticmethod
    def info(parent: QWidget, message: str) -> None:
        QMessageBox.information(parent, "Information", message)
