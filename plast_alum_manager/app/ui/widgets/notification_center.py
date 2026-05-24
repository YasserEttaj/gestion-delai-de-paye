from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.ui.icons import (
    BELL_ICON,
    COLOR_DANGER,
    COLOR_MUTED_DARK,
    COLOR_MUTED_LIGHT,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    PAID_ICON,
    RESET_ICON,
    VIEW_ICON,
    WARNING_ICON,
    app_icon,
)
from app.ui.widgets.modern_button import ModernButton


class NotificationCenterDialog(QDialog):
    open_requested = pyqtSignal(dict)
    mark_read_requested = pyqtSignal(str)
    mark_all_read_requested = pyqtSignal()
    snooze_requested = pyqtSignal(str)
    dismiss_requested = pyqtSignal(str)
    enable_desktop_requested = pyqtSignal()

    LEVEL_COLORS = {
        "normal": COLOR_SUCCESS,
        "attention": COLOR_WARNING,
        "urgent": COLOR_DANGER,
        "critical": "#7F1D1D",
        "info": COLOR_PRIMARY,
    }
    LEVEL_LABELS = {
        "normal": "Normal",
        "attention": "Attention",
        "urgent": "Urgent",
        "critical": "Critique",
        "info": "Info",
    }

    def __init__(self, alerts: list[dict], permission_state: str, desktop_enabled: bool, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Centre des alertes")
        self.setMinimumSize(720, 560)
        self.resize(820, 620)
        self.alerts: list[dict] = []
        self.permission_state = permission_state
        self.desktop_enabled = desktop_enabled

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        header = QHBoxLayout()
        self.title = QLabel("Centre des alertes")
        self.title.setProperty("heading", True)
        header.addWidget(self.title)
        header.addStretch(1)
        self.mark_all = ModernButton("Tout lu", "secondary", icon_name=PAID_ICON)
        self.mark_all.clicked.connect(self.mark_all_read_requested.emit)
        header.addWidget(self.mark_all)
        layout.addLayout(header)

        self.permission_banner = QFrame()
        self.permission_banner.setObjectName("NotificationPermissionBanner")
        self.permission_banner.setProperty("card", True)
        banner_layout = QHBoxLayout(self.permission_banner)
        banner_layout.setContentsMargins(12, 10, 12, 10)
        self.permission_text = QLabel()
        self.permission_text.setWordWrap(True)
        banner_layout.addWidget(self.permission_text, 1)
        self.enable_desktop = ModernButton("Activer", "primary", icon_name=BELL_ICON)
        self.enable_desktop.clicked.connect(self.enable_desktop_requested.emit)
        banner_layout.addWidget(self.enable_desktop)
        layout.addWidget(self.permission_banner)

        self.summary = QLabel()
        self.summary.setProperty("muted", True)
        layout.addWidget(self.summary)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(10)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll, 1)

        footer = QHBoxLayout()
        footer.addStretch(1)
        close = ModernButton("Fermer", "secondary")
        close.clicked.connect(self.accept)
        footer.addWidget(close)
        layout.addLayout(footer)
        self.reload(alerts, permission_state, desktop_enabled)

    def reload(self, alerts: list[dict], permission_state: str, desktop_enabled: bool) -> None:
        self.alerts = alerts
        self.permission_state = permission_state
        self.desktop_enabled = desktop_enabled
        self._render_permission()
        self._render_alerts()

    def _render_permission(self) -> None:
        if self.permission_state == "granted" and self.desktop_enabled:
            self.permission_banner.setVisible(False)
            return
        self.permission_banner.setVisible(True)
        if self.permission_state == "denied":
            self.permission_text.setText("Notifications bureau désactivées. Les alertes restent visibles dans l'application.")
            self.enable_desktop.setText("Réactiver")
        else:
            self.permission_text.setText("Autoriser TheCrownVibe à afficher les alertes importantes sur le bureau.")
            self.enable_desktop.setText("Autoriser")

    def _clear_alerts(self) -> None:
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _render_alerts(self) -> None:
        self._clear_alerts()
        unread = sum(1 for alert in self.alerts if not alert.get("read"))
        self.summary.setText(f"{len(self.alerts)} alerte(s) active(s) • {unread} non lue(s)")
        self.mark_all.setEnabled(bool(unread))
        if not self.alerts:
            empty = QLabel("Aucune alerte active.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setMinimumHeight(180)
            empty.setProperty("muted", True)
            self.list_layout.addWidget(empty)
            self.list_layout.addStretch(1)
            return
        for alert in self.alerts:
            self.list_layout.addWidget(self._card(alert))
        self.list_layout.addStretch(1)

    def _card(self, alert: dict) -> QFrame:
        level = alert.get("level", "info")
        color = self.LEVEL_COLORS.get(level, COLOR_PRIMARY)
        card = QFrame()
        card.setObjectName("NotificationCenterCard")
        card.setStyleSheet(
            f"""
            QFrame#NotificationCenterCard {{
                border-left: 4px solid {color};
                border-radius: 10px;
            }}
            """
        )
        card.setProperty("card", True)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(13, 11, 13, 11)
        layout.setSpacing(8)

        header = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        icon_label.setPixmap(app_icon(WARNING_ICON if level in {"attention", "urgent", "critical"} else BELL_ICON, color, 19).pixmap(19, 19))
        header.addWidget(icon_label)
        title = QLabel(alert.get("title", "Notification"))
        title.setStyleSheet("font-weight: 900;")
        header.addWidget(title, 1)
        badge = QLabel(self.LEVEL_LABELS.get(level, level.title()))
        badge.setStyleSheet(f"color: {color}; font-weight: 900;")
        header.addWidget(badge)
        if alert.get("read"):
            read = QLabel("Lu")
            read.setProperty("muted", True)
            header.addWidget(read)
        layout.addLayout(header)

        message = QLabel(alert.get("message", ""))
        message.setWordWrap(True)
        message.setProperty("muted", True)
        layout.addWidget(message)

        actions = QHBoxLayout()
        actions.addStretch(1)
        if alert.get("invoice_id") or alert.get("convention_id"):
            open_button = ModernButton("Ouvrir", "primary", icon_name=VIEW_ICON, compact=True)
            open_button.clicked.connect(lambda _=False, payload=dict(alert): self.open_requested.emit(payload))
            actions.addWidget(open_button)
        if not alert.get("read"):
            read_button = ModernButton("Lu", "secondary", icon_name=PAID_ICON, compact=True)
            read_button.clicked.connect(lambda _=False, key=alert["key"]: self.mark_read_requested.emit(key))
            actions.addWidget(read_button)
        snooze = ModernButton("Rappeler", "secondary", icon_name=RESET_ICON, compact=True)
        snooze.clicked.connect(lambda _=False, key=alert["key"]: self.snooze_requested.emit(key))
        actions.addWidget(snooze)
        dismiss = ModernButton("Ignorer", "danger", icon_name="x-circle", compact=True)
        dismiss.clicked.connect(lambda _=False, key=alert["key"]: self.dismiss_requested.emit(key))
        actions.addWidget(dismiss)
        layout.addLayout(actions)
        return card
