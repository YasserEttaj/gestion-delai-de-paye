from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QWidget

from app.ui.icons import (
    BELL_ICON,
    COLOR_MUTED_DARK,
    COLOR_MUTED_LIGHT,
    LANGUAGE_ICON,
    MOON_ICON,
    SEARCH_ICON,
    SUN_ICON,
    USER_ICON,
    app_icon,
    icon_pixmap,
)
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
        self.search_action = self.search_input.addAction(app_icon(SEARCH_ICON, COLOR_MUTED_DARK, 16), QLineEdit.ActionPosition.LeadingPosition)
        self.search_input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_input)

        self.language_combo = QComboBox()
        self.language_combo.setMinimumWidth(70)
        self.language_combo.addItem(app_icon(LANGUAGE_ICON, COLOR_MUTED_DARK, 16), "FR", "fr")
        self.language_combo.addItem(app_icon(LANGUAGE_ICON, COLOR_MUTED_DARK, 16), "EN", "en")
        self.language_combo.setToolTip("Langue")
        self.language_combo.currentIndexChanged.connect(lambda: self.language_changed.emit(self.language_combo.currentData()))
        layout.addWidget(self.language_combo)

        self.theme_button = ModernButton("Mode clair", "secondary", icon_name=SUN_ICON, tooltip="Changer de thème")
        self.theme_button.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_button)

        self.notification_button = ModernButton("0", "secondary", icon_name=BELL_ICON, tooltip="Notifications")
        self.notification_button.clicked.connect(self.notifications_requested.emit)
        layout.addWidget(self.notification_button)

        self.clock_label = QLabel()
        self.clock_label.setProperty("muted", True)
        layout.addWidget(self.clock_label)

        self.profile_icon = QLabel()
        self.profile_icon.setFixedSize(22, 22)
        layout.addWidget(self.profile_icon)

        self.profile_label = QLabel(user_name)
        self.profile_label.setObjectName("UserProfileLabel")
        self.profile_label.setStyleSheet("font-weight:800;")
        layout.addWidget(self.profile_label)

        self.current_theme = "dark"
        self._refresh_icons()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)
        self._tick()

    def _tick(self) -> None:
        self.clock_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M"))

    def _toggle_theme(self) -> None:
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self._refresh_icons()
        self.theme_changed.emit(self.current_theme)

    def set_title(self, title: str) -> None:
        self.title_label.setText(title)

    def set_notification_count(self, count: int) -> None:
        self.notification_button.setText(str(count))
        self.notification_button.setToolTip(f"{count} notification(s)")

    def set_theme(self, theme: str) -> None:
        self.current_theme = "light" if theme == "light" else "dark"
        self._refresh_icons()

    def set_language(self, language: str) -> None:
        index = self.language_combo.findData(language)
        if index >= 0:
            self.language_combo.blockSignals(True)
            self.language_combo.setCurrentIndex(index)
            self.language_combo.blockSignals(False)

    def _icon_color(self) -> str:
        return COLOR_MUTED_LIGHT if self.current_theme == "light" else COLOR_MUTED_DARK

    def _refresh_icons(self) -> None:
        color = self._icon_color()
        self.search_action.setIcon(app_icon(SEARCH_ICON, color, 16))
        for index in range(self.language_combo.count()):
            self.language_combo.setItemIcon(index, app_icon(LANGUAGE_ICON, color, 16))
        theme_icon = MOON_ICON if self.current_theme == "light" else SUN_ICON
        self.theme_button.setText("Mode sombre" if self.current_theme == "light" else "Mode clair")
        self.theme_button.set_app_icon(theme_icon, color, 17)
        self.notification_button.set_app_icon(BELL_ICON, color, 17)
        self.profile_icon.setPixmap(icon_pixmap(USER_ICON, color, 19))
