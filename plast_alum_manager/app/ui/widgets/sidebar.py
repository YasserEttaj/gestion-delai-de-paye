from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from app.ui.icons import (
    ACTIVITY_LOGS_ICON,
    COLOR_MUTED_DARK,
    COLOR_MUTED_LIGHT,
    COLOR_PRIMARY,
    COLOR_WHITE,
    CONVENTIONS_ICON,
    DASHBOARD_ICON,
    IMPORT_ICON,
    INVOICE_ADD_ICON,
    INVOICES_ICON,
    LOGOUT_ICON,
    REPORTS_ICON,
    SETTINGS_ICON,
    SUPPLIERS_ICON,
    USERS_ICON,
)
from app.ui.widgets.modern_button import ModernButton
from config import COMPANY_NAME, LOGO_PATH


class Sidebar(QWidget):
    page_requested = pyqtSignal(str)
    logout_requested = pyqtSignal()

    MENU = [
        ("dashboard", DASHBOARD_ICON, "Tableau de bord"),
        ("suppliers", SUPPLIERS_ICON, "Fournisseurs"),
        ("invoices", INVOICES_ICON, "Factures"),
        ("invoice_form", INVOICE_ADD_ICON, "Ajouter facture"),
        ("conventions", CONVENTIONS_ICON, "Conventions"),
        ("reports", REPORTS_ICON, "Rapports"),
        ("import_excel", IMPORT_ICON, "Import Excel"),
        ("users", USERS_ICON, "Utilisateurs"),
        ("settings", SETTINGS_ICON, "Paramètres"),
        ("activity_logs", ACTIVITY_LOGS_ICON, "Journal d’activité"),
    ]

    def __init__(self, allowed_pages: set[str], parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.buttons: dict[str, ModernButton] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 20, 18, 18)
        layout.setSpacing(8)

        logo = QLabel(COMPANY_NAME)
        if LOGO_PATH.exists():
            logo.setPixmap(QPixmap(str(LOGO_PATH)).scaledToWidth(175, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setStyleSheet("font-size:22px; font-weight:900;")
        layout.addWidget(logo)
        subtitle = QLabel("Paiements fournisseurs")
        subtitle.setProperty("muted", True)
        layout.addWidget(subtitle)
        layout.addSpacing(14)

        for page, icon, label in self.MENU:
            if page not in allowed_pages:
                continue
            button = ModernButton(label, "ghost", icon_name=icon, tooltip=label)
            button.setProperty("nav", True)
            button.setMinimumHeight(44)
            button.set_app_icon(icon, self._nav_icon_color(False), 19)
            button.clicked.connect(lambda _checked=False, key=page: self.page_requested.emit(key))
            layout.addWidget(button)
            self.buttons[page] = button

        layout.addStretch(1)
        logout = ModernButton("Déconnexion", "danger", icon_name=LOGOUT_ICON, tooltip="Déconnexion")
        logout.setProperty("logout", True)
        logout.setMinimumHeight(46)
        logout.set_app_icon(LOGOUT_ICON, COLOR_WHITE, 19)
        logout.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout)

    def _theme(self) -> str:
        app = QApplication.instance()
        return str(app.property("theme") if app else "dark")

    def _nav_icon_color(self, active: bool) -> str:
        if active:
            return COLOR_WHITE if self._theme() == "dark" else COLOR_PRIMARY
        return COLOR_MUTED_DARK if self._theme() == "dark" else COLOR_MUTED_LIGHT

    def set_active(self, page: str) -> None:
        for key, button in self.buttons.items():
            active = key == page
            button.setProperty("active", active)
            icon_name = next((icon for menu_page, icon, _label in self.MENU if menu_page == key), None)
            if icon_name:
                button.set_app_icon(icon_name, self._nav_icon_color(active), 19)
            button.style().unpolish(button)
            button.style().polish(button)

    def refresh_icons(self) -> None:
        active_page = next((key for key, button in self.buttons.items() if button.property("active")), "")
        self.set_active(active_page)
