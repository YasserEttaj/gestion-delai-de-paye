from __future__ import annotations

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QHeaderView, QLabel, QVBoxLayout, QWidget

from app.services.excel_service import ExcelService
from app.ui.widgets.confirm_dialog import ConfirmDialog
from app.ui.widgets.modern_button import ModernButton
from app.ui.widgets.modern_table import ModernTable


class ImportExcelPage(QWidget):
    def __init__(self, user, parent=None) -> None:
        super().__init__(parent)
        self.user = user
        self.preview: dict | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        top = QHBoxLayout()
        title = QLabel("Import Excel")
        title.setProperty("heading", True)
        top.addWidget(title)
        top.addStretch(1)
        choose = ModernButton("Choisir fichier Excel", "primary")
        choose.setEnabled(self.user.can_import_export)
        choose.clicked.connect(self.choose_file)
        self.import_button = ModernButton("Importer les lignes valides", "success")
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self.import_rows)
        top.addWidget(choose)
        top.addWidget(self.import_button)
        layout.addLayout(top)

        self.summary = QLabel("Colonnes attendues: " + ", ".join(ExcelService.EXPECTED_COLUMNS))
        self.summary.setProperty("muted", True)
        layout.addWidget(self.summary)

        self.table = ModernTable()
        self.table.set_headers(["Ligne", "Fournisseur", "Facture", "Date", "TTC", "Statut", "Erreurs"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)

    def choose_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choisir fichier Excel", "", "Excel (*.xlsx *.xlsm)")
        if not path:
            return
        try:
            self.preview = ExcelService.preview_import(path)
            self.render()
        except Exception as exc:
            ConfirmDialog.error(self, "Import Excel", str(exc))

    def render(self) -> None:
        if not self.preview:
            return
        rows = self.preview.get("rows", [])
        self.table.clearSpans()
        if not rows:
            self.table.show_empty("Aucune ligne à prévisualiser.", 7)
            return
        valid = sum(1 for row in rows if not row["errors"])
        invalid = len(rows) - valid
        global_errors = self.preview.get("errors", [])
        self.summary.setText(f"{len(rows)} ligne(s) lues • {valid} valide(s) • {invalid} invalide(s)" + (f" • {', '.join(global_errors)}" if global_errors else ""))
        self.import_button.setEnabled(valid > 0 and self.user.can_import_export)
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            values = [
                row["line"],
                row["supplier_name"],
                row["invoice_number"],
                row["invoice_date"],
                f"{row['amount_ttc']:,.2f}",
                row["status"],
                "; ".join(row["errors"]),
            ]
            for col, value in enumerate(values):
                self.table.set_text_item(row_idx, col, value, align_right=col in {0, 4})
                item = self.table.item(row_idx, col)
                if item and row["errors"]:
                    item.setBackground(QColor("#FEE2E2"))

    def import_rows(self) -> None:
        if not self.preview:
            return
        if not ConfirmDialog.ask(self, "Confirmation", "Créer automatiquement les fournisseurs manquants et importer les lignes valides ?"):
            return
        try:
            result = ExcelService.import_valid_rows(self.preview, self.user.id, create_suppliers=True)
            ConfirmDialog.info(self, "Import Excel", f"{result['imported']} importée(s), {result['skipped']} ignorée(s).")
            self.preview = None
            self.import_button.setEnabled(False)
            self.table.setRowCount(0)
        except Exception as exc:
            ConfirmDialog.error(self, "Import Excel", str(exc))
