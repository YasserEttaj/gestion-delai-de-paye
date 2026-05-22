from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QDate, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from app.services.invoice_service import InvoiceService
from app.services.supplier_service import SupplierService
from app.ui.pages.invoice_form_page import InvoiceFormDialog, PaymentDialog
from app.ui.widgets.confirm_dialog import ConfirmDialog
from app.ui.widgets.modern_button import ModernButton
from app.ui.widgets.modern_table import ModernTable
from config import STATUS_LABELS_FR, STATUS_PAID, STATUS_PARTIAL, STATUS_UNPAID


class InvoicesPage(QWidget):
    def __init__(self, user, parent=None) -> None:
        super().__init__(parent)
        self.user = user
        self.rows: list[dict] = []
        self.current_page = 0
        self.page_size = 15
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        top = QHBoxLayout()
        title = QLabel("Gestion des factures fournisseurs")
        title.setProperty("heading", True)
        top.addWidget(title)
        top.addStretch(1)
        add = ModernButton("Ajouter facture", "primary")
        add.setEnabled(self.user.can_edit)
        add.clicked.connect(self.add_invoice)
        top.addWidget(add)
        layout.addLayout(top)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Recherche fournisseur ou numéro facture")
        self.search.textChanged.connect(self.refresh)
        self.status = QComboBox()
        self.status.addItem("Tous statuts", "")
        self.status.addItem(STATUS_LABELS_FR[STATUS_UNPAID], STATUS_UNPAID)
        self.status.addItem(STATUS_LABELS_FR[STATUS_PARTIAL], STATUS_PARTIAL)
        self.status.addItem(STATUS_LABELS_FR[STATUS_PAID], STATUS_PAID)
        self.status.currentIndexChanged.connect(self.refresh)
        self.deadline = QComboBox()
        self.deadline.addItem("Tous délais", "")
        for key, label in [("normal", "Normal"), ("attention", "Attention"), ("urgent", "Urgent"), ("critical", "Critique")]:
            self.deadline.addItem(label, key)
        self.deadline.currentIndexChanged.connect(self.refresh)
        self.supplier = QComboBox()
        self.supplier.addItem("Tous fournisseurs", "")
        self.supplier.currentIndexChanged.connect(self.refresh)
        self.sort = QComboBox()
        self.sort.addItem("Date récente", "date_desc")
        self.sort.addItem("Date ancienne", "date_asc")
        self.sort.addItem("Montant", "amount")
        self.sort.addItem("Nombre de jours", "days")
        self.sort.currentIndexChanged.connect(self.refresh)
        filters.addWidget(self.search, 2)
        filters.addWidget(self.status)
        filters.addWidget(self.deadline)
        filters.addWidget(self.supplier)
        filters.addWidget(self.sort)
        layout.addLayout(filters)

        self.table = ModernTable()
        self.table.set_headers(["ID", "Fournisseur", "N° facture", "Date", "Réception", "TTC", "Statut", "Paiement", "Jours", "Délai", "PJ", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)

        pager = QHBoxLayout()
        self.prev_button = ModernButton("Précédent", "secondary")
        self.next_button = ModernButton("Suivant", "secondary")
        self.page_label = QLabel()
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        pager.addStretch(1)
        pager.addWidget(self.prev_button)
        pager.addWidget(self.page_label)
        pager.addWidget(self.next_button)
        layout.addLayout(pager)
        self.reload_suppliers()
        self.refresh()

    def reload_suppliers(self) -> None:
        current = self.supplier.currentData()
        self.supplier.blockSignals(True)
        self.supplier.clear()
        self.supplier.addItem("Tous fournisseurs", "")
        for supplier in SupplierService.get_all():
            self.supplier.addItem(supplier.name, supplier.id)
        index = self.supplier.findData(current)
        if index >= 0:
            self.supplier.setCurrentIndex(index)
        self.supplier.blockSignals(False)

    def set_supplier_filter(self, supplier_id: int) -> None:
        index = self.supplier.findData(supplier_id)
        if index >= 0:
            self.supplier.setCurrentIndex(index)
        self.refresh()

    def filters(self) -> dict:
        return {
            "search": self.search.text(),
            "status": self.status.currentData(),
            "deadline_category": self.deadline.currentData(),
            "supplier_id": self.supplier.currentData(),
            "sort_by": self.sort.currentData(),
        }

    def refresh(self) -> None:
        self.rows = InvoiceService.list_invoices(self.filters())
        self.current_page = min(self.current_page, max((len(self.rows) - 1) // self.page_size, 0))
        self.render()

    def render(self) -> None:
        self.table.clearSpans()
        start = self.current_page * self.page_size
        page_rows = self.rows[start : start + self.page_size]
        if not page_rows:
            self.table.show_empty("Aucune facture trouvée.", 12)
            self.page_label.setText("Page 1/1 • 0 factures")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return
        self.table.setRowCount(len(page_rows))
        status_colors = {STATUS_PAID: "#22C55E", STATUS_UNPAID: "#EF4444", STATUS_PARTIAL: "#F59E0B"}
        for row_idx, row in enumerate(page_rows):
            invoice = row["invoice"]
            values = [
                invoice.id,
                row["supplier"].name,
                invoice.invoice_number,
                invoice.invoice_date,
                invoice.reception_date or "",
                f"{float(invoice.amount_ttc or 0):,.2f}",
            ]
            for col, value in enumerate(values):
                self.table.set_text_item(row_idx, col, value, align_right=col in {0, 5})
            self.table.setCellWidget(row_idx, 6, self.table.badge(STATUS_LABELS_FR.get(invoice.status, invoice.status), status_colors.get(invoice.status, "#64748B")))
            self.table.set_text_item(row_idx, 7, invoice.payment_date or "")
            self.table.set_text_item(row_idx, 8, row["deadline"].days, align_right=True)
            badge = self.table.badge(row["deadline"].label, row["deadline"].color)
            badge.setToolTip(row["deadline"].tooltip)
            self.table.setCellWidget(row_idx, 9, badge)
            self.table.set_text_item(row_idx, 10, "Oui" if invoice.attachment_path else "Non")
            action_box = QWidget()
            h = QHBoxLayout(action_box)
            h.setContentsMargins(0, 0, 0, 0)
            view = ModernButton("Voir", "secondary")
            view.clicked.connect(lambda _=False, iid=invoice.id: self.view_invoice(iid))
            edit = ModernButton("Éditer", "secondary")
            edit.setEnabled(self.user.can_edit)
            edit.clicked.connect(lambda _=False, iid=invoice.id: self.edit_invoice(iid))
            pay = ModernButton("Payer", "success")
            pay.setEnabled(self.user.can_edit and invoice.status != STATUS_PAID)
            pay.clicked.connect(lambda _=False, iid=invoice.id: self.add_payment(iid))
            attach = ModernButton("PJ", "secondary")
            attach.clicked.connect(lambda _=False, path=invoice.attachment_path: self.open_attachment(path))
            delete = ModernButton("Supprimer", "danger")
            delete.setEnabled(self.user.can_delete)
            delete.clicked.connect(lambda _=False, iid=invoice.id: self.delete_invoice(iid))
            for button in (view, edit, pay, attach, delete):
                h.addWidget(button)
            self.table.setCellWidget(row_idx, 11, action_box)
        total_pages = max((len(self.rows) - 1) // self.page_size + 1, 1)
        self.page_label.setText(f"Page {self.current_page + 1}/{total_pages} • {len(self.rows)} factures")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page + 1 < total_pages)

    def prev_page(self) -> None:
        self.current_page = max(self.current_page - 1, 0)
        self.render()

    def next_page(self) -> None:
        self.current_page += 1
        self.render()

    def add_invoice(self) -> None:
        dialog = InvoiceFormDialog(parent=self)
        if dialog.exec():
            try:
                InvoiceService.create_invoice(dialog.data(), self.user.id)
                self.reload_suppliers()
                self.refresh()
            except Exception as exc:
                ConfirmDialog.error(self, "Erreur", str(exc))

    def edit_invoice(self, invoice_id: int) -> None:
        invoice = InvoiceService.get_invoice(invoice_id)
        if not invoice:
            return
        dialog = InvoiceFormDialog(invoice, self)
        if dialog.exec():
            try:
                InvoiceService.update_invoice(invoice_id, dialog.data(), self.user.id)
                self.reload_suppliers()
                self.refresh()
            except Exception as exc:
                ConfirmDialog.error(self, "Erreur", str(exc))

    def add_payment(self, invoice_id: int) -> None:
        invoice = InvoiceService.get_invoice(invoice_id)
        if not invoice:
            return
        dialog = PaymentDialog(invoice, self)
        if dialog.exec():
            data = dialog.data()
            try:
                InvoiceService.add_payment(invoice_id, data["amount"], data["payment_date"], data["payment_method"], data["reference"], data["notes"], self.user.id)
                self.refresh()
            except Exception as exc:
                ConfirmDialog.error(self, "Erreur", str(exc))

    def delete_invoice(self, invoice_id: int) -> None:
        if not ConfirmDialog.ask(self, "Confirmation", "Supprimer cette facture ?"):
            return
        try:
            InvoiceService.delete_invoice(invoice_id, self.user.id)
            self.refresh()
        except Exception as exc:
            ConfirmDialog.error(self, "Erreur", str(exc))

    def view_invoice(self, invoice_id: int) -> None:
        invoice = InvoiceService.get_invoice(invoice_id)
        if not invoice:
            return
        deadline = next((row["deadline"] for row in InvoiceService.list_invoices({}) if row["invoice"].id == invoice_id), None)
        ConfirmDialog.info(
            self,
            f"Facture {invoice.invoice_number}",
            f"Fournisseur: {invoice.supplier.name}\nDate facture: {invoice.invoice_date}\nMontant TTC: {float(invoice.amount_ttc or 0):,.2f} MAD\nStatut: {STATUS_LABELS_FR.get(invoice.status, invoice.status)}\nDélai: {deadline.label if deadline else '-'}\nNotes: {invoice.notes or '-'}",
        )

    def open_attachment(self, path: str | None) -> None:
        if not path:
            ConfirmDialog.error(self, "Pièce jointe", "Aucune pièce jointe pour cette facture.")
            return
        file_path = Path(path)
        if not file_path.exists():
            ConfirmDialog.error(self, "Pièce jointe", "Le fichier est introuvable.")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(file_path)))
