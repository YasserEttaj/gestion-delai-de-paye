from __future__ import annotations

from datetime import datetime

from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.services.activity_service import ActivityService
from app.services.user_service import UserService
from app.ui.widgets.confirm_dialog import ConfirmDialog
from app.ui.widgets.modern_button import ModernButton
from app.ui.widgets.modern_table import ModernTable
from config import EXPORT_DIR


class ActivityLogsPage(QWidget):
    def __init__(self, user, parent=None) -> None:
        super().__init__(parent)
        self.user = user
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        top = QHBoxLayout()
        title = QLabel("Journal d'activité")
        title.setProperty("heading", True)
        top.addWidget(title)
        top.addStretch(1)
        export = ModernButton("Exporter logs", "secondary")
        export.clicked.connect(self.export_logs)
        top.addWidget(export)
        layout.addLayout(top)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Recherche")
        self.search.textChanged.connect(self.refresh)
        self.user_filter = QComboBox()
        self.user_filter.addItem("Tous utilisateurs", "")
        for item in UserService.list_users():
            self.user_filter.addItem(item.username, item.id)
        self.user_filter.currentIndexChanged.connect(self.refresh)
        self.action = QLineEdit()
        self.action.setPlaceholderText("Action")
        self.action.textChanged.connect(self.refresh)
        filters.addWidget(self.search, 2)
        filters.addWidget(self.user_filter)
        filters.addWidget(self.action)
        layout.addLayout(filters)

        self.table = ModernTable()
        self.table.set_headers(["ID", "Date", "Utilisateur", "Action", "Entité", "ID entité", "Détails"])
        layout.addWidget(self.table, 1)
        self.logs = []
        self.refresh()

    def filters(self) -> dict:
        return {
            "search": self.search.text(),
            "user_id": self.user_filter.currentData(),
            "action": self.action.text(),
        }

    def refresh(self) -> None:
        self.logs = ActivityService.list_logs(self.filters())
        self.table.clearSpans()
        if not self.logs:
            self.table.show_empty("Aucune activité trouvée.", 7)
            return
        self.table.setRowCount(len(self.logs))
        for row, log in enumerate(self.logs):
            values = [log.id, log.created_at, log.user.username if log.user else "Système", log.action, log.entity_type or "", log.entity_id or "", log.details or ""]
            for col, value in enumerate(values):
                self.table.set_text_item(row, col, value, align_right=col in {0, 5})

    def export_logs(self) -> None:
        from openpyxl import Workbook

        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        path = EXPORT_DIR / f"journal_activite_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.title = "Journal"
        ws.append(["ID", "Date", "Utilisateur", "Action", "Entité", "ID entité", "Détails"])
        for log in self.logs:
            ws.append([log.id, log.created_at, log.user.username if log.user else "Système", log.action, log.entity_type, log.entity_id, log.details])
        wb.save(path)
        ConfirmDialog.info(self, "Export logs", f"Fichier créé: {path}")
