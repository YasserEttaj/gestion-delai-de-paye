from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QVBoxLayout

from app.models.supplier_model import Supplier
from app.ui.icons import COLOR_MUTED_LIGHT, COLOR_PRIMARY, SAVE_ICON, UNPAID_ICON, app_icon


class SupplierFormDialog(QDialog):
    def __init__(self, supplier: Supplier | None = None, parent=None) -> None:
        super().__init__(parent)
        self.supplier = supplier
        self.setWindowTitle("Fournisseur")
        self.setMinimumWidth(620)
        layout = QVBoxLayout(self)
        title = QLabel("Informations fournisseur")
        title.setProperty("heading", True)
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(form.labelAlignment())
        self.name = QLineEdit()
        self.name.setPlaceholderText("Nom fournisseur *")
        self.ice = QLineEdit()
        self.if_number = QLineEdit()
        self.rc = QLineEdit()
        self.address = QTextEdit()
        self.address.setFixedHeight(70)
        self.city = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.contact_person = QLineEdit()
        self.rib = QLineEdit()
        self.notes = QTextEdit()
        self.notes.setFixedHeight(80)

        form.addRow("Nom fournisseur *", self.name)
        form.addRow("ICE", self.ice)
        form.addRow("IF", self.if_number)
        form.addRow("RC", self.rc)
        form.addRow("Adresse", self.address)
        form.addRow("Ville", self.city)
        form.addRow("Téléphone", self.phone)
        form.addRow("Email", self.email)
        form.addRow("Personne de contact", self.contact_person)
        form.addRow("RIB", self.rib)
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

        if supplier:
            self._load(supplier)

    def _load(self, supplier: Supplier) -> None:
        self.name.setText(supplier.name or "")
        self.ice.setText(supplier.ice or "")
        self.if_number.setText(supplier.if_number or "")
        self.rc.setText(supplier.rc or "")
        self.address.setPlainText(supplier.address or "")
        self.city.setText(supplier.city or "")
        self.phone.setText(supplier.phone or "")
        self.email.setText(supplier.email or "")
        self.contact_person.setText(supplier.contact_person or "")
        self.rib.setText(supplier.rib or "")
        self.notes.setPlainText(supplier.notes or "")

    def accept(self) -> None:
        if not self.name.text().strip():
            self.error.setText("Le nom fournisseur est obligatoire.")
            return
        super().accept()

    def data(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "ice": self.ice.text().strip() or None,
            "if_number": self.if_number.text().strip() or None,
            "rc": self.rc.text().strip() or None,
            "address": self.address.toPlainText().strip() or None,
            "city": self.city.text().strip() or None,
            "phone": self.phone.text().strip() or None,
            "email": self.email.text().strip() or None,
            "contact_person": self.contact_person.text().strip() or None,
            "rib": self.rib.text().strip() or None,
            "notes": self.notes.toPlainText().strip() or None,
        }
