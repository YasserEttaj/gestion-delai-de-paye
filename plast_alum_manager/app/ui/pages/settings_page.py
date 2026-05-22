from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QAbstractSpinBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.services.backup_service import BackupService
from app.services.settings_service import SettingsService
from app.ui.widgets.confirm_dialog import ConfirmDialog
from app.ui.widgets.modern_button import ModernButton
from config import USER_LOGO_PATH


class SettingsPage(QWidget):
    def __init__(self, user, parent=None) -> None:
        super().__init__(parent)
        self.user = user
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        title = QLabel("Paramètres")
        title.setProperty("heading", True)
        layout.addWidget(title)

        form = QFormLayout()
        form.setHorizontalSpacing(34)
        form.setVerticalSpacing(12)
        self.company_name = QLineEdit()
        self.app_title = QLineEdit()
        self.language = QComboBox()
        self.language.addItem("Français", "fr")
        self.language.addItem("العربية", "ar")
        self.theme = QComboBox()
        self.theme.addItem("Sombre", "dark")
        self.theme.addItem("Clair", "light")
        self.currency = QComboBox()
        self.currency.addItems(["MAD", "DHS"])
        self.date_format = QLineEdit()
        self.logo_path = QLineEdit()
        self.backup_folder = QLineEdit()
        self.auto_backup = QCheckBox("Créer une sauvegarde à la fermeture")
        self.keep = QSpinBox()
        self.keep.setRange(1, 100)
        self.high_unpaid = QSpinBox()
        self.high_unpaid.setRange(0, 999999999)
        self.normal_max = QSpinBox()
        self.normal_max.setRange(1, 365)
        self.attention_min = QSpinBox()
        self.attention_min.setRange(1, 365)
        self.attention_max = QSpinBox()
        self.attention_max.setRange(1, 365)
        self.urgent_min = QSpinBox()
        self.urgent_min.setRange(1, 365)
        self.urgent_max = QSpinBox()
        self.urgent_max.setRange(1, 365)
        self.critical_min = QSpinBox()
        self.critical_min.setRange(1, 365)

        for field in (
            self.company_name,
            self.app_title,
            self.language,
            self.theme,
            self.currency,
            self.date_format,
            self.logo_path,
            self.backup_folder,
            self.keep,
            self.high_unpaid,
            self.normal_max,
            self.attention_min,
            self.attention_max,
            self.urgent_min,
            self.urgent_max,
            self.critical_min,
        ):
            field.setMaximumWidth(860)

        for spin in (
            self.keep,
            self.high_unpaid,
            self.normal_max,
            self.attention_min,
            self.attention_max,
            self.urgent_min,
            self.urgent_max,
            self.critical_min,
        ):
            spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        logo_row = QHBoxLayout()
        logo_row.addWidget(self.logo_path, 1)
        logo_btn = ModernButton("Choisir", "secondary")
        logo_btn.clicked.connect(self.choose_logo)
        logo_row.addWidget(logo_btn)

        form.addRow("Société", self.company_name)
        form.addRow("Titre application", self.app_title)
        form.addRow("Langue par défaut", self.language)
        form.addRow("Thème par défaut", self.theme)
        form.addRow("Devise", self.currency)
        form.addRow("Format date", self.date_format)
        form.addRow("Logo", logo_row)
        form.addRow("Dossier sauvegarde", self.backup_folder)
        form.addRow("", self.auto_backup)
        form.addRow("Sauvegardes à garder", self.keep)
        form.addRow("Alerte montant impayé", self.high_unpaid)
        form.addRow("Normal max jours", self.normal_max)
        form.addRow("Attention min", self.attention_min)
        form.addRow("Attention max", self.attention_max)
        form.addRow("Urgent min", self.urgent_min)
        form.addRow("Urgent max", self.urgent_max)
        form.addRow("Critique min", self.critical_min)
        layout.addLayout(form)

        actions = QHBoxLayout()
        save = ModernButton("Enregistrer paramètres", "primary")
        save.setEnabled(self.user.can_manage_users)
        save.clicked.connect(self.save)
        backup = ModernButton("Créer sauvegarde", "success")
        backup.clicked.connect(self.create_backup)
        restore = ModernButton("Restaurer sauvegarde", "danger")
        restore.setEnabled(self.user.can_manage_users)
        restore.clicked.connect(self.restore_backup)
        actions.addWidget(save)
        actions.addWidget(backup)
        actions.addWidget(restore)
        actions.addStretch(1)
        layout.addLayout(actions)
        layout.addStretch(1)
        self.load()

    def load(self) -> None:
        settings = SettingsService.all()
        self.company_name.setText(settings.get("company_name", "PLAST ALUM"))
        self.app_title.setText(settings.get("app_title", "PLAST ALUM"))
        self.language.setCurrentIndex(max(self.language.findData(settings.get("default_language", "fr")), 0))
        self.theme.setCurrentIndex(max(self.theme.findData(settings.get("default_theme", "dark")), 0))
        self.currency.setCurrentText(settings.get("currency", "MAD"))
        self.date_format.setText(settings.get("date_format", "%d/%m/%Y"))
        self.logo_path.setText(settings.get("logo_path", ""))
        self.backup_folder.setText(settings.get("backup_folder", "data/backups"))
        self.auto_backup.setChecked(settings.get("auto_backup_on_close", "true") == "true")
        self.keep.setValue(int(settings.get("auto_backup_keep", 10)))
        self.high_unpaid.setValue(int(float(settings.get("high_unpaid_amount", 50000))))
        self.normal_max.setValue(int(settings.get("normal_max_days", 40)))
        self.attention_min.setValue(int(settings.get("attention_min_days", 41)))
        self.attention_max.setValue(int(settings.get("attention_max_days", 49)))
        self.urgent_min.setValue(int(settings.get("urgent_min_days", 50)))
        self.urgent_max.setValue(int(settings.get("urgent_max_days", 59)))
        self.critical_min.setValue(int(settings.get("critical_min_days", 60)))

    def values(self) -> dict[str, str]:
        return {
            "company_name": self.company_name.text().strip(),
            "app_title": self.app_title.text().strip(),
            "default_language": self.language.currentData(),
            "default_theme": self.theme.currentData(),
            "currency": self.currency.currentText(),
            "date_format": self.date_format.text().strip(),
            "logo_path": self.logo_path.text().strip(),
            "backup_folder": self.backup_folder.text().strip(),
            "auto_backup_on_close": "true" if self.auto_backup.isChecked() else "false",
            "auto_backup_keep": str(self.keep.value()),
            "high_unpaid_amount": str(self.high_unpaid.value()),
            "normal_max_days": str(self.normal_max.value()),
            "attention_min_days": str(self.attention_min.value()),
            "attention_max_days": str(self.attention_max.value()),
            "urgent_min_days": str(self.urgent_min.value()),
            "urgent_max_days": str(self.urgent_max.value()),
            "critical_min_days": str(self.critical_min.value()),
        }

    def choose_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choisir logo", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            try:
                from PIL import Image

                USER_LOGO_PATH.parent.mkdir(parents=True, exist_ok=True)
                Image.open(path).save(USER_LOGO_PATH)
                self.logo_path.setText(str(USER_LOGO_PATH))
            except Exception as exc:
                ConfirmDialog.error(self, "Logo", f"Impossible de copier le logo: {exc}")

    def save(self) -> None:
        try:
            SettingsService.set_many(self.values(), self.user.id)
            ConfirmDialog.info(self, "Paramètres", "Paramètres enregistrés. Certains changements s'appliquent après redémarrage.")
        except Exception as exc:
            ConfirmDialog.error(self, "Paramètres", str(exc))

    def create_backup(self) -> None:
        try:
            path = BackupService.create_backup(self.user.id, self.keep.value())
            ConfirmDialog.info(self, "Sauvegarde", f"Sauvegarde créée: {path}")
        except Exception as exc:
            ConfirmDialog.error(self, "Sauvegarde", str(exc))

    def restore_backup(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choisir sauvegarde", "", "SQLite (*.sqlite)")
        if not path:
            return
        if not ConfirmDialog.ask(self, "Restauration", "Restaurer cette sauvegarde ? L'application doit être relancée ensuite."):
            return
        try:
            BackupService.restore_backup(path, self.user.id)
            ConfirmDialog.info(self, "Restauration", "Sauvegarde restaurée. Relancez l'application.")
        except Exception as exc:
            ConfirmDialog.error(self, "Restauration", str(exc))
