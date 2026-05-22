from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QComboBox, QVBoxLayout, QWidget

from app.services.supplier_service import SupplierService
from app.ui.pages.supplier_form_page import SupplierFormDialog
from app.ui.widgets.confirm_dialog import ConfirmDialog
from app.ui.widgets.modern_button import ModernButton
from app.ui.widgets.modern_table import ModernTable
from config import EXPORT_DIR


class SuppliersPage(QWidget):
    supplier_invoices_requested = pyqtSignal(int)

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
        title = QLabel("Gestion des fournisseurs")
        title.setProperty("heading", True)
        top.addWidget(title)
        top.addStretch(1)
        self.add_button = ModernButton("Ajouter fournisseur", "primary")
        self.add_button.clicked.connect(self.add_supplier)
        self.add_button.setEnabled(self.user.can_edit)
        top.addWidget(self.add_button)
        export = ModernButton("Exporter fournisseurs", "secondary")
        export.clicked.connect(self.export_suppliers)
        top.addWidget(export)
        layout.addLayout(top)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Recherche nom, ICE, téléphone, ville")
        self.search.textChanged.connect(self.refresh)
        self.city = QComboBox()
        self.city.addItem("Toutes les villes", "")
        self.city.currentIndexChanged.connect(self.refresh)
        self.sort = QComboBox()
        self.sort.addItem("Nom", "name")
        self.sort.addItem("Date création", "date")
        self.sort.addItem("Ville", "city")
        self.sort.currentIndexChanged.connect(self.refresh)
        filters.addWidget(self.search, 2)
        filters.addWidget(self.city)
        filters.addWidget(self.sort)
        layout.addLayout(filters)

        self.table = ModernTable()
        self.table.set_headers(["ID", "Nom fournisseur", "ICE", "Ville", "Téléphone", "Email", "RIB", "Factures", "Impayé", "Actions"])
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
        self.reload_cities()
        self.refresh()

    def reload_cities(self) -> None:
        current = self.city.currentData()
        self.city.blockSignals(True)
        self.city.clear()
        self.city.addItem("Toutes les villes", "")
        for city in SupplierService.get_cities():
            self.city.addItem(city, city)
        index = self.city.findData(current)
        if index >= 0:
            self.city.setCurrentIndex(index)
        self.city.blockSignals(False)

    def refresh(self) -> None:
        self.rows = SupplierService.list_suppliers(self.search.text(), self.city.currentData() or "", self.sort.currentData())
        self.current_page = min(self.current_page, max((len(self.rows) - 1) // self.page_size, 0))
        self.render()

    def render(self) -> None:
        self.table.clearSpans()
        start = self.current_page * self.page_size
        page_rows = self.rows[start : start + self.page_size]
        if not page_rows:
            self.table.show_empty("Aucun fournisseur trouvé.", 10)
            self.page_label.setText("Page 1/1 • 0 fournisseurs")
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return
        self.table.setRowCount(len(page_rows))
        for row_idx, row in enumerate(page_rows):
            supplier = row["supplier"]
            values = [
                supplier.id,
                supplier.name,
                supplier.ice or "",
                supplier.city or "",
                supplier.phone or "",
                supplier.email or "",
                supplier.rib or "",
                row["invoice_count"],
                f"{row['unpaid_amount']:,.2f}",
            ]
            for col, value in enumerate(values):
                self.table.set_text_item(row_idx, col, value, align_right=col in {0, 7, 8})
            action_box = QWidget()
            h = QHBoxLayout(action_box)
            h.setContentsMargins(0, 0, 0, 0)
            view = ModernButton("Voir", "secondary")
            view.clicked.connect(lambda _=False, sid=supplier.id: self.view_supplier(sid))
            edit = ModernButton("Éditer", "secondary")
            edit.setEnabled(self.user.can_edit)
            edit.clicked.connect(lambda _=False, sid=supplier.id: self.edit_supplier(sid))
            delete = ModernButton("Supprimer", "danger")
            delete.setEnabled(self.user.can_delete)
            delete.clicked.connect(lambda _=False, sid=supplier.id: self.delete_supplier(sid))
            invoices = ModernButton("Factures", "secondary")
            invoices.clicked.connect(lambda _=False, sid=supplier.id: self.supplier_invoices_requested.emit(sid))
            for button in (view, edit, invoices, delete):
                h.addWidget(button)
            self.table.setCellWidget(row_idx, 9, action_box)
        total_pages = max((len(self.rows) - 1) // self.page_size + 1, 1)
        self.page_label.setText(f"Page {self.current_page + 1}/{total_pages} • {len(self.rows)} fournisseurs")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page + 1 < total_pages)

    def prev_page(self) -> None:
        self.current_page = max(self.current_page - 1, 0)
        self.render()

    def next_page(self) -> None:
        self.current_page += 1
        self.render()

    def add_supplier(self) -> None:
        dialog = SupplierFormDialog(parent=self)
        if dialog.exec():
            try:
                SupplierService.create_supplier(dialog.data(), self.user.id)
                self.reload_cities()
                self.refresh()
            except Exception as exc:
                ConfirmDialog.error(self, "Erreur", str(exc))

    def edit_supplier(self, supplier_id: int) -> None:
        supplier = SupplierService.get_supplier(supplier_id)
        if not supplier:
            return
        dialog = SupplierFormDialog(supplier, self)
        if dialog.exec():
            try:
                SupplierService.update_supplier(supplier_id, dialog.data(), self.user.id)
                self.reload_cities()
                self.refresh()
            except Exception as exc:
                ConfirmDialog.error(self, "Erreur", str(exc))

    def delete_supplier(self, supplier_id: int) -> None:
        if not ConfirmDialog.ask(self, "Confirmation", "Supprimer ce fournisseur et ses factures ?"):
            return
        try:
            SupplierService.delete_supplier(supplier_id, self.user.id)
            self.reload_cities()
            self.refresh()
        except Exception as exc:
            ConfirmDialog.error(self, "Erreur", str(exc))

    def view_supplier(self, supplier_id: int) -> None:
        rows = SupplierService.list_suppliers()
        row = next((item for item in rows if item["supplier"].id == supplier_id), None)
        if not row:
            return
        supplier = row["supplier"]
        ConfirmDialog.info(
            self,
            supplier.name,
            f"ICE: {supplier.ice or '-'}\nVille: {supplier.city or '-'}\nTéléphone: {supplier.phone or '-'}\nEmail: {supplier.email or '-'}\nFactures: {row['invoice_count']}\nImpayé: {row['unpaid_amount']:,.2f} MAD",
        )

    def export_suppliers(self) -> None:
        from openpyxl import Workbook

        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        path = EXPORT_DIR / f"fournisseurs_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.title = "Fournisseurs"
        ws.append(["ID", "Nom", "ICE", "Ville", "Téléphone", "Email", "RIB", "Factures", "Impayé"])
        for row in self.rows:
            supplier = row["supplier"]
            ws.append([supplier.id, supplier.name, supplier.ice, supplier.city, supplier.phone, supplier.email, supplier.rib, row["invoice_count"], row["unpaid_amount"]])
        wb.save(path)
        ConfirmDialog.info(self, "Export", f"Fichier créé: {path}")
