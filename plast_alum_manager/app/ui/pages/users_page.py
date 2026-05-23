from __future__ import annotations

from PyQt6.QtWidgets import QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.models.user_model import User
from app.services.user_service import UserService
from app.ui.widgets.confirm_dialog import ConfirmDialog
from app.ui.widgets.modern_button import ModernButton
from app.ui.widgets.modern_table import ModernTable
from config import ROLE_ADMIN, ROLE_USER


class UserDialog(QDialog):
    def __init__(self, user: User | None = None, parent=None) -> None:
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Utilisateur")
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.full_name = QLineEdit()
        self.username = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.role = QComboBox()
        self.role.addItems([ROLE_ADMIN, ROLE_USER])
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.active = QCheckBox("Actif")
        self.active.setChecked(True)
        form.addRow("Nom complet *", self.full_name)
        form.addRow("Utilisateur *", self.username)
        form.addRow("Email", self.email)
        form.addRow("Téléphone", self.phone)
        form.addRow("Rôle", self.role)
        form.addRow("Mot de passe" + (" *" if not user else ""), self.password)
        form.addRow("", self.active)
        layout.addLayout(form)
        self.error = QLabel("")
        self.error.setStyleSheet("color:#EF4444; font-weight:700;")
        layout.addWidget(self.error)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Enregistrer")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        if user:
            self.full_name.setText(user.full_name or "")
            self.username.setText(user.username or "")
            self.email.setText(user.email or "")
            self.phone.setText(user.phone or "")
            idx = self.role.findText(user.role)
            if idx >= 0:
                self.role.setCurrentIndex(idx)
            self.active.setChecked(bool(user.is_active))

    def accept(self) -> None:
        if not self.full_name.text().strip() or not self.username.text().strip():
            self.error.setText("Nom complet et utilisateur sont obligatoires.")
            return
        if not self.user and not self.password.text():
            self.error.setText("Le mot de passe est obligatoire.")
            return
        if self.password.text() and len(self.password.text()) < 8:
            self.error.setText("Mot de passe faible: utilisez au moins 8 caractères.")
            return
        super().accept()

    def data(self) -> dict:
        return {
            "full_name": self.full_name.text().strip(),
            "username": self.username.text().strip(),
            "email": self.email.text().strip() or None,
            "phone": self.phone.text().strip() or None,
            "role": self.role.currentText(),
            "password": self.password.text(),
            "is_active": self.active.isChecked(),
        }


class UsersPage(QWidget):
    def __init__(self, user, parent=None) -> None:
        super().__init__(parent)
        self.user = user
        self.users: list[User] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        top = QHBoxLayout()
        title = QLabel("Gestion des utilisateurs")
        title.setProperty("heading", True)
        top.addWidget(title)
        top.addStretch(1)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Recherche utilisateur")
        self.search.textChanged.connect(self.refresh)
        top.addWidget(self.search)
        add = ModernButton("Ajouter utilisateur", "primary")
        add.clicked.connect(self.add_user)
        top.addWidget(add)
        layout.addLayout(top)
        self.table = ModernTable()
        self.table.set_headers(["ID", "Nom", "Utilisateur", "Email", "Téléphone", "Rôle", "Actif", "Dernière connexion", "Actions"])
        layout.addWidget(self.table, 1)
        self.refresh()

    def refresh(self) -> None:
        self.users = UserService.list_users(self.search.text())
        self.table.setRowCount(len(self.users))
        for row, user in enumerate(self.users):
            values = [
                user.id,
                user.full_name,
                user.username,
                user.email or "",
                user.phone or "",
                user.role,
                "Oui" if user.is_active else "Non",
                user.last_login or "",
            ]
            for col, value in enumerate(values):
                self.table.set_text_item(row, col, value, align_right=col == 0)
            box = QWidget()
            h = QHBoxLayout(box)
            h.setContentsMargins(0, 0, 0, 0)
            edit = ModernButton("Éditer", "secondary")
            edit.clicked.connect(lambda _=False, uid=user.id: self.edit_user(uid))
            delete = ModernButton("Supprimer", "danger")
            delete.setEnabled(user.id != self.user.id)
            delete.clicked.connect(lambda _=False, uid=user.id: self.delete_user(uid))
            h.addWidget(edit)
            h.addWidget(delete)
            self.table.setCellWidget(row, 8, box)

    def add_user(self) -> None:
        dialog = UserDialog(parent=self)
        if dialog.exec():
            try:
                UserService.create_user(dialog.data(), self.user.id)
                self.refresh()
            except Exception as exc:
                ConfirmDialog.error(self, "Erreur", str(exc))

    def edit_user(self, user_id: int) -> None:
        user = next((item for item in self.users if item.id == user_id), None)
        if not user:
            return
        dialog = UserDialog(user, self)
        if dialog.exec():
            try:
                UserService.update_user(user_id, dialog.data(), self.user.id)
                self.refresh()
            except Exception as exc:
                ConfirmDialog.error(self, "Erreur", str(exc))

    def delete_user(self, user_id: int) -> None:
        if not ConfirmDialog.ask(self, "Confirmation", "Supprimer cet utilisateur ?"):
            return
        try:
            UserService.delete_user(user_id, self.user.id)
            self.refresh()
        except Exception as exc:
            ConfirmDialog.error(self, "Erreur", str(exc))
