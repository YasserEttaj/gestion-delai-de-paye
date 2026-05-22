from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.widgets.modern_button import ModernButton
from config import COMPANY_NAME, LOGO_PATH


class Sidebar(QWidget):
    page_requested = pyqtSignal(str)
    logout_requested = pyqtSignal()

    MENU = [
        ("dashboard", "⌂", "Tableau de bord"),
        ("suppliers", "◇", "Fournisseurs"),
        ("invoices", "▤", "Factures"),
        ("invoice_form", "+", "Ajouter facture"),
        ("reports", "↧", "Rapports"),
        ("import_excel", "⇪", "Import Excel"),
        ("users", "◉", "Utilisateurs"),
        ("settings", "⚙", "Paramètres"),
        ("activity_logs", "≡", "Journal d’activité"),
    ]

    def __init__(self, allowed_pages: set[str], parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.buttons: dict[str, ModernButton] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(7)

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
            button = ModernButton(f"{icon}  {label}", "ghost")
            button.setProperty("nav", True)
            button.setMinimumHeight(44)
            button.clicked.connect(lambda _checked=False, key=page: self.page_requested.emit(key))
            layout.addWidget(button)
            self.buttons[page] = button

        layout.addStretch(1)
        logout = ModernButton("↪  Déconnexion", "danger")
        logout.setProperty("logout", True)
        logout.setMinimumHeight(46)
        logout.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout)

    def set_active(self, page: str) -> None:
        for key, button in self.buttons.items():
            button.setProperty("active", key == page)
            button.style().unpolish(button)
            button.style().polish(button)
