from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QPushButton

from app.ui.icons import COLOR_MUTED_DARK, COLOR_MUTED_LIGHT, COLOR_WHITE, app_icon, icon_size


class ModernButton(QPushButton):
    def __init__(self, text: str = "", role: str = "secondary", parent=None, icon_name: str | None = None, tooltip: str | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(38)
        self._icon_name: str | None = None
        self._icon_size = 17
        self.set_role(role)
        if icon_name:
            self.set_app_icon(icon_name)
        if tooltip:
            self.setToolTip(tooltip)

    def set_role(self, role: str) -> None:
        self.setProperty("role", role)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_app_icon(self, icon_name: str, color: str | None = None, size: int = 17) -> None:
        role = self.property("role")
        if color is None:
            app = QApplication.instance()
            theme = app.property("theme") if app else "dark"
            color = COLOR_WHITE if role in {"primary", "success", "warning", "danger"} else (COLOR_MUTED_LIGHT if theme == "light" else COLOR_MUTED_DARK)
        self._icon_name = icon_name
        self._icon_size = size
        self.setIcon(app_icon(icon_name, color, size))
        self.setIconSize(icon_size(size))

    def refresh_icon_theme(self) -> None:
        if self._icon_name:
            self.set_app_icon(self._icon_name, None, self._icon_size)
