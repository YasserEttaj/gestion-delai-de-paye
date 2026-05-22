from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QWidget

from app.ui.widgets.modern_button import ModernButton


class Topbar(QWidget):
    search_changed = pyqtSignal(str)
    language_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    notifications_requested = pyqtSignal()

    def __init__(self, user_name: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Topbar")
        self.setMinimumHeight(76)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 12, 22, 12)
        layout.setSpacing(12)

        self.title_label = QLabel("Tableau de bord")
        self.title_label.setProperty("heading", True)
        layout.addWidget(self.title_label)
        layout.addStretch(1)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Recherche globale")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumWidth(220)
        self.search_input.setMaximumWidth(320)
        self.search_input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_input)

        self.language_combo = QComboBox()
        self.language_combo.setMinimumWidth(70)
        self.language_combo.addItem("FR", "fr")
        self.language_combo.addItem("AR", "ar")
        self.language_combo.currentIndexChanged.connect(lambda: self.language_changed.emit(self.language_combo.currentData()))
        layout.addWidget(self.language_combo)

        self.theme_button = ModernButton("Mode clair", "secondary")
        self.theme_button.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_button)

        self.notification_button = ModernButton("🔔 0", "secondary")
        self.notification_button.clicked.connect(self.notifications_requested.emit)
        layout.addWidget(self.notification_button)

        self.clock_label = QLabel()
        self.clock_label.setProperty("muted", True)
        layout.addWidget(self.clock_label)

        self.profile_label = QLabel(user_name)
        self.profile_label.setObjectName("UserProfileLabel")
        self.profile_label.setStyleSheet("font-weight:800;")
        layout.addWidget(self.profile_label)

        self.current_theme = "dark"
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)
        self._tick()

    def _tick(self) -> None:
        self.clock_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M"))

    def _toggle_theme(self) -> None:
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.theme_button.setText("Mode sombre" if self.current_theme == "light" else "Mode clair")
        self.theme_changed.emit(self.current_theme)

    def set_title(self, title: str) -> None:
        self.title_label.setText(title)

    def set_notification_count(self, count: int) -> None:
        self.notification_button.setText(f"🔔 {count}")

    def set_theme(self, theme: str) -> None:
        self.current_theme = "light" if theme == "light" else "dark"
        self.theme_button.setText("Mode sombre" if self.current_theme == "light" else "Mode clair")

    def set_language(self, language: str) -> None:
        index = self.language_combo.findData(language)
        if index >= 0:
            self.language_combo.blockSignals(True)
            self.language_combo.setCurrentIndex(index)
            self.language_combo.blockSignals(False)
