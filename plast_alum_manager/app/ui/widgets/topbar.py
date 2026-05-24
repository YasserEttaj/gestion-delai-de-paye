from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QWidget

from app.ui.icons import (
    BELL_ICON,
    COLOR_MUTED_DARK,
    COLOR_MUTED_LIGHT,
    COLOR_WHITE,
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

    TEXTS = {
        "fr": {
            "global_search": "Recherche globale",
            "language": "Langue",
            "switch_language": "Changer de langue",
            "change_theme": "Changer de thème",
            "light_mode": "Mode clair",
            "dark_mode": "Mode sombre",
            "notifications": "Notifications",
        },
        "en": {
            "global_search": "Global search",
            "language": "Language",
            "switch_language": "Switch language",
            "change_theme": "Change theme",
            "light_mode": "Light mode",
            "dark_mode": "Dark mode",
            "notifications": "Notifications",
        },
    }

    def __init__(self, user_name: str, parent=None) -> None:
        super().__init__(parent)
        self.ui_language = "fr"
        self.current_language = "fr"
        self.notification_count = 0
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
        self.search_input.setPlaceholderText(self._text("global_search"))
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumWidth(220)
        self.search_input.setMaximumWidth(320)
        self.search_action = self.search_input.addAction(app_icon(SEARCH_ICON, COLOR_MUTED_DARK, 16), QLineEdit.ActionPosition.LeadingPosition)
        self.search_input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_input)

        self.language_button = ModernButton("FR", "secondary", icon_name=LANGUAGE_ICON, tooltip=self._text("switch_language"))
        self.language_button.setObjectName("LanguageSwitchButton")
        self.language_button.setFixedWidth(74)
        self.language_button.setMinimumHeight(38)
        self.language_button.clicked.connect(self._toggle_language)
        layout.addWidget(self.language_button)

        self.theme_button = ModernButton(self._text("light_mode"), "secondary", icon_name=SUN_ICON, tooltip=self._text("change_theme"))
        self.theme_button.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_button)

        self.notification_button = ModernButton("0", "secondary", icon_name=BELL_ICON, tooltip=self._text("notifications"))
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

    def _text(self, key: str) -> str:
        return self.TEXTS.get(self.ui_language, self.TEXTS["fr"]).get(key, key)

    def _tick(self) -> None:
        self.clock_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M"))

    def _toggle_theme(self) -> None:
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self._refresh_icons()
        self.theme_changed.emit(self.current_theme)

    def _toggle_language(self) -> None:
        language = "en" if self.current_language == "fr" else "fr"
        self.set_language(language)
        self.language_changed.emit(language)

    def set_title(self, title: str) -> None:
        self.title_label.setText(title)

    def set_notification_count(self, count: int) -> None:
        self.notification_count = count
        self.notification_button.setText(str(count))
        self.notification_button.setToolTip(f"{count} {self._text('notifications').lower()}")
        self.notification_button.set_role("warning" if count else "secondary")
        self._refresh_icons()

    def set_theme(self, theme: str) -> None:
        self.current_theme = "light" if theme == "light" else "dark"
        self._refresh_icons()

    def set_language(self, language: str) -> None:
        self.current_language = "en" if language == "en" else "fr"
        self.language_button.setText(self.current_language.upper())

    def set_ui_language(self, language: str) -> None:
        self.ui_language = "en" if language == "en" else "fr"
        self.search_input.setPlaceholderText(self._text("global_search"))
        self.language_button.setToolTip(self._text("switch_language"))
        self.theme_button.setToolTip(self._text("change_theme"))
        self.set_notification_count(self.notification_count)
        self._refresh_icons()

    def _icon_color(self) -> str:
        return COLOR_MUTED_LIGHT if self.current_theme == "light" else COLOR_MUTED_DARK

    def _refresh_icons(self) -> None:
        color = self._icon_color()
        self.search_action.setIcon(app_icon(SEARCH_ICON, color, 16))
        self.language_button.set_app_icon(LANGUAGE_ICON, color, 17)
        theme_icon = MOON_ICON if self.current_theme == "light" else SUN_ICON
        self.theme_button.setText(self._text("dark_mode") if self.current_theme == "light" else self._text("light_mode"))
        self.theme_button.set_app_icon(theme_icon, color, 17)
        notification_color = COLOR_WHITE if self.notification_count else color
        self.notification_button.set_app_icon(BELL_ICON, notification_color, 17)
        self.profile_icon.setPixmap(icon_pixmap(USER_ICON, color, 19))
