from __future__ import annotations

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.services.excel_service import ExcelService
from app.services.pdf_service import PdfService
from app.services.report_service import ReportService
from app.services.supplier_service import SupplierService
from app.ui.widgets.confirm_dialog import ConfirmDialog
from app.ui.widgets.modern_button import ModernButton
from app.ui.widgets.modern_table import ModernTable
from config import STATUS_LABELS_FR, STATUS_PAID, STATUS_PARTIAL, STATUS_UNPAID


class ReportsPage(QWidget):
    def __init__(self, user, parent=None) -> None:
        super().__init__(parent)
        self.user = user
        self.report = {"rows": [], "count": 0, "total_amount": 0, "total_paid": 0, "total_unpaid": 0}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        top = QHBoxLayout()
        title = QLabel("Rapports et exports")
        title.setProperty("heading", True)
        top.addWidget(title)
        top.addStretch(1)
        excel = ModernButton("Export Excel", "success")
        excel.setEnabled(self.user.can_import_export)
        excel.clicked.connect(self.export_excel)
        pdf = ModernButton("Export PDF", "danger")
        pdf.setEnabled(self.user.can_import_export)
        pdf.clicked.connect(self.export_pdf)
        print_button = ModernButton("Imprimer", "secondary")
        print_button.setEnabled(self.user.can_import_export)
        print_button.clicked.connect(self.print_report)
        top.addWidget(excel)
        top.addWidget(pdf)
        top.addWidget(print_button)
        layout.addLayout(top)

        filters = QVBoxLayout()
        primary_filters = QHBoxLayout()
        secondary_filters = QHBoxLayout()
        self.report_type = QComboBox()
        self.report_type.setMinimumWidth(210)
        for label, data in [
            ("Toutes les factures", {}),
            ("Factures payées", {"status": STATUS_PAID}),
            ("Factures non payées", {"status": STATUS_UNPAID}),
            ("Factures partiellement payées", {"status": STATUS_PARTIAL}),
            ("Factures critiques +60 jours", {"deadline_category": "critical"}),
            ("Montant impayé par fournisseur", {}),
            ("Rapport mensuel", {}),
            ("Rapport des délais de paiement", {}),
        ]:
            self.report_type.addItem(label, data)
        self.report_type.currentIndexChanged.connect(self.refresh)
        self.supplier = QComboBox()
        self.supplier.setMinimumWidth(210)
        self.supplier.addItem("Tous fournisseurs", "")
        for supplier in SupplierService.get_all():
            self.supplier.addItem(supplier.name, supplier.id)
        self.supplier.currentIndexChanged.connect(self.refresh)
        self.status = QComboBox()
        self.status.setMinimumWidth(180)
        self.status.addItem("Tous statuts", "")
        self.status.addItem(STATUS_LABELS_FR[STATUS_PAID], STATUS_PAID)
        self.status.addItem(STATUS_LABELS_FR[STATUS_UNPAID], STATUS_UNPAID)
        self.status.addItem(STATUS_LABELS_FR[STATUS_PARTIAL], STATUS_PARTIAL)
        self.status.currentIndexChanged.connect(self.refresh)
        self.deadline = QComboBox()
        self.deadline.setMinimumWidth(150)
        self.deadline.addItem("Tous délais", "")
        for key, label in [("normal", "Normal"), ("attention", "Attention"), ("urgent", "Urgent"), ("critical", "Critique")]:
            self.deadline.addItem(label, key)
        self.deadline.currentIndexChanged.connect(self.refresh)
        self.date_from = QLineEdit()
        self.date_from.setPlaceholderText("Du yyyy-mm-dd")
        self.date_from.setMinimumWidth(170)
        self.date_from.textChanged.connect(self.refresh)
        self.date_to = QLineEdit()
        self.date_to.setPlaceholderText("Au yyyy-mm-dd")
        self.date_to.setMinimumWidth(170)
        self.date_to.textChanged.connect(self.refresh)
        self.amount_min = QLineEdit()
        self.amount_min.setPlaceholderText("Min")
        self.amount_min.setMinimumWidth(90)
        self.amount_min.textChanged.connect(self.refresh)
        self.amount_max = QLineEdit()
        self.amount_max.setPlaceholderText("Max")
        self.amount_max.setMinimumWidth(90)
        self.amount_max.textChanged.connect(self.refresh)
        for widget in (self.report_type, self.supplier, self.status, self.deadline):
            primary_filters.addWidget(widget)
        primary_filters.addStretch(1)
        for widget in (self.date_from, self.date_to, self.amount_min, self.amount_max):
            secondary_filters.addWidget(widget)
        secondary_filters.addStretch(1)
        filters.addLayout(primary_filters)
        filters.addLayout(secondary_filters)
        layout.addLayout(filters)

        self.summary = QLabel()
        self.summary.setStyleSheet("font-weight:800;")
        layout.addWidget(self.summary)

        self.table = ModernTable()
        self.table.set_headers(["ID", "Fournisseur", "Facture", "Date", "TTC", "Statut", "Jours", "Délai", "Payé", "Reste"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)
        self.refresh()

    def filters(self) -> dict:
        data = dict(self.report_type.currentData() or {})
        if self.supplier.currentData():
            data["supplier_id"] = self.supplier.currentData()
        if self.status.currentData():
            data["status"] = self.status.currentData()
        if self.deadline.currentData():
            data["deadline_category"] = self.deadline.currentData()
        if self.date_from.text().strip():
            data["date_from"] = self.date_from.text().strip()
        if self.date_to.text().strip():
            data["date_to"] = self.date_to.text().strip()
        if self.amount_min.text().strip():
            data["amount_min"] = self.amount_min.text().strip()
        if self.amount_max.text().strip():
            data["amount_max"] = self.amount_max.text().strip()
        return data

    def refresh(self) -> None:
        try:
            self.report = ReportService.filtered_report(self.filters())
        except Exception as exc:
            self.report = {"rows": [], "count": 0, "total_amount": 0, "total_paid": 0, "total_unpaid": 0}
            self.summary.setText(f"Impossible de charger le rapport: {exc}")
            self.table.show_empty("Aucune donnée disponible.", 10)
            return
        self.summary.setText(
            f"{self.report['count']} facture(s) • Total: {self.report['total_amount']:,.2f} MAD • Payé: {self.report['total_paid']:,.2f} MAD • Impayé: {self.report['total_unpaid']:,.2f} MAD"
        )
        self.table.clearSpans()
        rows = self.report["rows"]
        if not rows:
            self.table.show_empty("Aucune donnée pour les filtres sélectionnés.", 10)
            return
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            invoice = row["invoice"]
            values = [
                invoice.id,
                row["supplier"].name,
                invoice.invoice_number,
                invoice.invoice_date,
                f"{float(invoice.amount_ttc or 0):,.2f}",
                STATUS_LABELS_FR.get(invoice.status, invoice.status),
                row["deadline"].days,
                row["deadline"].label,
                f"{row['paid_amount']:,.2f}",
                f"{row['outstanding_amount']:,.2f}",
            ]
            for col, value in enumerate(values):
                self.table.set_text_item(row_idx, col, value, align_right=col in {0, 4, 6, 8, 9})

    def export_excel(self) -> None:
        if not self.user.can_import_export:
            ConfirmDialog.error(self, "Accès refusé", "Vous n'êtes pas autorisé à exporter les rapports.")
            return
        try:
            path = ExcelService.export_invoices(self.report["rows"], user_id=self.user.id)
            ConfirmDialog.info(self, "Export Excel", f"Fichier créé: {path}")
        except Exception as exc:
            ConfirmDialog.error(self, "Export Excel", str(exc))

    def export_pdf(self) -> None:
        if not self.user.can_import_export:
            ConfirmDialog.error(self, "Accès refusé", "Vous n'êtes pas autorisé à exporter les rapports.")
            return
        try:
            path = PdfService.export_report(self.report, self.report_type.currentText(), self.filters(), self.user.full_name, self.user.id)
            ConfirmDialog.info(self, "Export PDF", f"Fichier créé: {path}")
        except Exception as exc:
            ConfirmDialog.error(self, "Export PDF", str(exc))

    def print_report(self) -> None:
        if not self.user.can_import_export:
            ConfirmDialog.error(self, "Accès refusé", "Vous n'êtes pas autorisé à imprimer les rapports.")
            return
        try:
            path = PdfService.export_report(self.report, self.report_type.currentText(), self.filters(), self.user.full_name, self.user.id)
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        except Exception as exc:
            ConfirmDialog.error(self, "Impression", str(exc))
