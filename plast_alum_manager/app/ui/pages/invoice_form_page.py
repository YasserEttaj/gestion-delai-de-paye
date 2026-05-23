from __future__ import annotations

from datetime import date

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QAbstractSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)

from app.models.invoice_model import Invoice
from app.services.deadline_service import DeadlineService
from app.services.supplier_service import SupplierService
from app.ui.icons import ATTACHMENT_ICON, COLOR_MUTED_LIGHT, COLOR_PRIMARY, SAVE_ICON, UNPAID_ICON, app_icon
from app.ui.widgets.modern_button import ModernButton
from config import PAYMENT_METHODS, STATUS_LABELS_FR, STATUS_PAID, STATUS_PARTIAL, STATUS_UNPAID


def _qdate_from_text(value: str | None) -> QDate:
    parsed = DeadlineService.parse_date(value)
    if not parsed:
        parsed = date.today()
    return QDate(parsed.year, parsed.month, parsed.day)


class InvoiceFormDialog(QDialog):
    def __init__(self, invoice: Invoice | None = None, parent=None) -> None:
        super().__init__(parent)
        self.invoice = invoice
        self.attachment_source: str | None = None
        self.suppliers = SupplierService.get_all()
        self.setWindowTitle("Facture fournisseur")
        self.setMinimumWidth(720)

        layout = QVBoxLayout(self)
        title = QLabel("Informations facture")
        title.setProperty("heading", True)
        layout.addWidget(title)

        form = QFormLayout()
        self.supplier = QComboBox()
        self.supplier.setEditable(False)
        self.supplier.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        for supplier in self.suppliers:
            self.supplier.addItem(supplier.name, supplier.id)
        self.invoice_number = QLineEdit()
        self.invoice_number.setPlaceholderText("Numéro facture *")
        self.invoice_date = QDateEdit()
        self.invoice_date.setCalendarPopup(True)
        self.invoice_date.setDate(QDate.currentDate())
        self.reception_date = QDateEdit()
        self.reception_date.setCalendarPopup(True)
        self.reception_date.setDate(QDate.currentDate())
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDate(QDate.currentDate().addDays(60))

        self.amount_ht = QDoubleSpinBox()
        self.amount_ht.setRange(0, 999999999)
        self.amount_ht.setDecimals(2)
        self.amount_ht.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.amount_ht.valueChanged.connect(self._recalculate)
        self.tva_rate = QDoubleSpinBox()
        self.tva_rate.setRange(0, 100)
        self.tva_rate.setDecimals(2)
        self.tva_rate.setValue(20)
        self.tva_rate.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.tva_rate.valueChanged.connect(self._recalculate)
        self.amount_tva = QDoubleSpinBox()
        self.amount_tva.setRange(0, 999999999)
        self.amount_tva.setDecimals(2)
        self.amount_tva.setReadOnly(True)
        self.amount_tva.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.amount_ttc = QDoubleSpinBox()
        self.amount_ttc.setRange(0, 999999999)
        self.amount_ttc.setDecimals(2)
        self.amount_ttc.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.status = QComboBox()
        self.status.addItem(STATUS_LABELS_FR[STATUS_UNPAID], STATUS_UNPAID)
        self.status.addItem(STATUS_LABELS_FR[STATUS_PARTIAL], STATUS_PARTIAL)
        self.status.addItem(STATUS_LABELS_FR[STATUS_PAID], STATUS_PAID)
        self.status.currentIndexChanged.connect(self._toggle_payment)
        self.payment_date = QDateEdit()
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setDate(QDate.currentDate())
        self.payment_method = QComboBox()
        self.payment_method.addItems(PAYMENT_METHODS)

        attachment_row = QHBoxLayout()
        self.attachment_label = QLabel("Aucune pièce jointe")
        browse = ModernButton("Choisir fichier", "secondary", icon_name=ATTACHMENT_ICON)
        browse.clicked.connect(self._choose_attachment)
        attachment_row.addWidget(self.attachment_label, 1)
        attachment_row.addWidget(browse)

        self.notes = QTextEdit()
        self.notes.setFixedHeight(80)

        form.addRow("Fournisseur *", self.supplier)
        form.addRow("Numéro facture *", self.invoice_number)
        form.addRow("Date facture *", self.invoice_date)
        form.addRow("Date réception", self.reception_date)
        form.addRow("Date échéance", self.due_date)
        form.addRow("Montant HT *", self.amount_ht)
        form.addRow("TVA %", self.tva_rate)
        form.addRow("Montant TVA", self.amount_tva)
        form.addRow("Montant TTC", self.amount_ttc)
        form.addRow("Statut", self.status)
        form.addRow("Date paiement", self.payment_date)
        form.addRow("Mode paiement", self.payment_method)
        form.addRow("Pièce jointe", attachment_row)
        form.addRow("Notes", self.notes)
        layout.addLayout(form)

        self.error = QLabel("")
        self.error.setStyleSheet("color:#EF4444; font-weight:700;")
        layout.addWidget(self.error)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Enregistrer")
        buttons.button(QDialogButtonBox.StandardButton.Save).setIcon(app_icon(SAVE_ICON, COLOR_PRIMARY, 16))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setIcon(app_icon(UNPAID_ICON, COLOR_MUTED_LIGHT, 16))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if invoice:
            self._load(invoice)
        self._toggle_payment()

    def _recalculate(self) -> None:
        ht = self.amount_ht.value()
        tva = ht * self.tva_rate.value() / 100
        self.amount_tva.blockSignals(True)
        self.amount_ttc.blockSignals(True)
        self.amount_tva.setValue(round(tva, 2))
        self.amount_ttc.setValue(round(ht + tva, 2))
        self.amount_tva.blockSignals(False)
        self.amount_ttc.blockSignals(False)

    def _toggle_payment(self) -> None:
        paid = self.status.currentData() == STATUS_PAID
        self.payment_date.setEnabled(paid)
        self.payment_method.setEnabled(paid)

    def _choose_attachment(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choisir une pièce jointe", "", "Documents (*.pdf *.jpg *.jpeg *.png)")
        if path:
            self.attachment_source = path
            self.attachment_label.setText(path)

    def _load(self, invoice: Invoice) -> None:
        index = self.supplier.findData(invoice.supplier_id)
        if index >= 0:
            self.supplier.setCurrentIndex(index)
        self.invoice_number.setText(invoice.invoice_number or "")
        self.invoice_date.setDate(_qdate_from_text(invoice.invoice_date))
        self.reception_date.setDate(_qdate_from_text(invoice.reception_date))
        self.due_date.setDate(_qdate_from_text(invoice.due_date))
        self.amount_ht.setValue(float(invoice.amount_ht or 0))
        self.tva_rate.setValue(float(invoice.tva_rate or 20))
        self.amount_tva.setValue(float(invoice.amount_tva or 0))
        self.amount_ttc.setValue(float(invoice.amount_ttc or 0))
        status_index = self.status.findData(invoice.status)
        if status_index >= 0:
            self.status.setCurrentIndex(status_index)
        self.payment_date.setDate(_qdate_from_text(invoice.payment_date))
        method_index = self.payment_method.findText(invoice.payment_method or "")
        if method_index >= 0:
            self.payment_method.setCurrentIndex(method_index)
        self.attachment_label.setText(invoice.attachment_path or "Aucune pièce jointe")
        self.notes.setPlainText(invoice.notes or "")

    def accept(self) -> None:
        if self.supplier.currentData() is None:
            self.error.setText("Le fournisseur est obligatoire.")
            return
        if not self.invoice_number.text().strip():
            self.error.setText("Le numéro de facture est obligatoire.")
            return
        if self.amount_ttc.value() <= 0:
            self.error.setText("Le montant doit être positif.")
            return
        if self.status.currentData() == STATUS_PAID and not self.payment_date.date().isValid():
            self.error.setText("La date paiement est obligatoire pour une facture payée.")
            return
        super().accept()

    def data(self) -> dict:
        return {
            "supplier_id": int(self.supplier.currentData()),
            "invoice_number": self.invoice_number.text().strip(),
            "invoice_date": self.invoice_date.date().toString("yyyy-MM-dd"),
            "reception_date": self.reception_date.date().toString("yyyy-MM-dd"),
            "due_date": self.due_date.date().toString("yyyy-MM-dd"),
            "amount_ht": float(self.amount_ht.value()),
            "tva_rate": float(self.tva_rate.value()),
            "amount_tva": float(self.amount_tva.value()),
            "amount_ttc": float(self.amount_ttc.value()),
            "status": self.status.currentData(),
            "payment_date": self.payment_date.date().toString("yyyy-MM-dd") if self.status.currentData() == STATUS_PAID else None,
            "payment_method": self.payment_method.currentText() if self.status.currentData() == STATUS_PAID else None,
            "attachment_source": self.attachment_source,
            "notes": self.notes.toPlainText().strip() or None,
        }


class PaymentDialog(QDialog):
    def __init__(self, invoice: Invoice, parent=None) -> None:
        super().__init__(parent)
        self.invoice = invoice
        paid = sum(float(payment.amount or 0) for payment in getattr(invoice, "payments", []))
        outstanding = max(float(invoice.amount_ttc or 0) - paid, 0.0)
        self.setWindowTitle("Paiement partiel")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.01, max(outstanding, 0.01))
        self.amount.setDecimals(2)
        self.amount.setValue(max(outstanding, 0.01))
        self.amount.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.payment_date = QDateEdit()
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setDate(QDate.currentDate())
        self.payment_method = QComboBox()
        self.payment_method.addItems(PAYMENT_METHODS)
        self.reference = QLineEdit()
        self.notes = QTextEdit()
        self.notes.setFixedHeight(70)
        form.addRow("Montant", self.amount)
        form.addRow("Date paiement", self.payment_date)
        form.addRow("Mode paiement", self.payment_method)
        form.addRow("Référence", self.reference)
        form.addRow("Notes", self.notes)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Enregistrer")
        buttons.button(QDialogButtonBox.StandardButton.Save).setIcon(app_icon(SAVE_ICON, COLOR_PRIMARY, 16))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setIcon(app_icon(UNPAID_ICON, COLOR_MUTED_LIGHT, 16))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def data(self) -> dict:
        return {
            "amount": float(self.amount.value()),
            "payment_date": self.payment_date.date().toString("yyyy-MM-dd"),
            "payment_method": self.payment_method.currentText(),
            "reference": self.reference.text().strip(),
            "notes": self.notes.toPlainText().strip(),
        }
