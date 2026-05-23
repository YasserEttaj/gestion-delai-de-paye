from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QVBoxLayout

from app.ui.icons import PAID_ICON, WARNING_ICON, app_icon


class NotificationCard(QFrame):
    COLORS = {
        "normal": "#22C55E",
        "attention": "#F59E0B",
        "urgent": "#EF4444",
        "critical": "#7F1D1D",
        "info": "#2563EB",
    }
    ICONS = {
        "normal": PAID_ICON,
        "attention": WARNING_ICON,
        "urgent": WARNING_ICON,
        "critical": WARNING_ICON,
        "info": "bell",
    }

    def __init__(self, title: str, message: str, level: str = "info", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("NotificationCard")
        color = self.COLORS.get(level, "#2563EB")
        theme = QApplication.instance().property("theme") if QApplication.instance() else "dark"
        if theme == "light":
            background = "#FFFFFF"
            border = "#DDE5F0"
        else:
            background = "#111D31"
            border = "#2F3D55"
        self.setStyleSheet(
            f"""
            QFrame#NotificationCard {{
                background: {background};
                border: 1px solid {border};
                border-left: 4px solid {color};
                border-radius: 9px;
            }}
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        header = QHBoxLayout()
        header.setSpacing(8)
        icon_label = QLabel()
        icon_label.setFixedSize(18, 18)
        icon_label.setPixmap(app_icon(self.ICONS.get(level, "bell"), color, 18).pixmap(18, 18))
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight:800;")
        header.addWidget(icon_label)
        header.addWidget(self.title_label, 1, Qt.AlignmentFlag.AlignVCenter)
        self.message_label = QLabel(message)
        self.message_label.setProperty("muted", True)
        self.message_label.setWordWrap(True)
        layout.addLayout(header)
        layout.addWidget(self.message_label)
