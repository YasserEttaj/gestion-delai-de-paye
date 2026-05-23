from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.services.backup_service import BackupService
from app.services.settings_service import SettingsService
from app.ui.icons import BACKUP_ICON, FOLDER_OPEN_ICON, RESET_ICON, SAVE_ICON
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

        scroll = QScrollArea()
        scroll.setObjectName("PageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        scroll.setWidget(container)
        content = QVBoxLayout(container)
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        card = QFrame()
        card.setObjectName("SettingsCard")
        card.setProperty("card", True)
        card.setMinimumWidth(900)
        card.setMaximumWidth(1320)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 20, 22, 20)
        card_layout.setSpacing(18)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(34)
        form.setVerticalSpacing(13)
        self.company_name = QLineEdit()
        self.app_title = QLineEdit()
        self.language = QComboBox()
        self.language.addItem("Français", "fr")
        self.language.addItem("English", "en")
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
            field.setMaximumWidth(940)
            field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

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

        logo_widget = QWidget()
        logo_widget.setMaximumWidth(940)
        logo_row = QHBoxLayout(logo_widget)
        logo_row.setContentsMargins(0, 0, 0, 0)
        logo_row.setSpacing(10)
        logo_row.addWidget(self.logo_path, 1)
        logo_btn = ModernButton("Choisir", "secondary", icon_name=FOLDER_OPEN_ICON)
        logo_btn.setFixedWidth(150)
        logo_btn.clicked.connect(self.choose_logo)
        logo_row.addWidget(logo_btn)

        form.addRow("Société", self.company_name)
        form.addRow("Titre application", self.app_title)
        form.addRow("Langue par défaut", self.language)
        form.addRow("Thème par défaut", self.theme)
        form.addRow("Devise", self.currency)
        form.addRow("Format date", self.date_format)
        form.addRow("Logo", logo_widget)
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
        card_layout.addLayout(form)

        actions = QHBoxLayout()
        save = ModernButton("Enregistrer paramètres", "primary", icon_name=SAVE_ICON)
        save.setEnabled(self.user.can_manage_users)
        save.clicked.connect(self.save)
        backup = ModernButton("Créer sauvegarde", "success", icon_name=BACKUP_ICON)
        backup.clicked.connect(self.create_backup)
        restore = ModernButton("Restaurer sauvegarde", "danger", icon_name=RESET_ICON)
        restore.setEnabled(self.user.can_manage_users)
        restore.clicked.connect(self.restore_backup)
        actions.addWidget(save)
        actions.addWidget(backup)
        actions.addWidget(restore)
        actions.addStretch(1)
        card_layout.addLayout(actions)
        content.addWidget(card, 0, Qt.AlignmentFlag.AlignTop)
        content.addStretch(1)
        layout.addWidget(scroll, 1)
        self.load()

    def load(self) -> None:
        settings = SettingsService.all()
        def as_int(key: str, default: int) -> int:
            try:
                return int(float(settings.get(key, default)))
            except (TypeError, ValueError):
                return default

        self.company_name.setText(settings.get("company_name", "PLAST ALUM"))
        self.app_title.setText(settings.get("app_title", "PLAST ALUM"))
        self.language.setCurrentIndex(max(self.language.findData(settings.get("default_language", "fr")), 0))
        self.theme.setCurrentIndex(max(self.theme.findData(settings.get("default_theme", "dark")), 0))
        self.currency.setCurrentText(settings.get("currency", "MAD"))
        self.date_format.setText(settings.get("date_format", "%d/%m/%Y"))
        self.logo_path.setText(settings.get("logo_path", ""))
        self.backup_folder.setText(settings.get("backup_folder", "data/backups"))
        self.backup_folder.setToolTip(self.backup_folder.text())
        self.auto_backup.setChecked(settings.get("auto_backup_on_close", "true") == "true")
        self.keep.setValue(as_int("auto_backup_keep", 10))
        self.high_unpaid.setValue(as_int("high_unpaid_amount", 50000))
        self.normal_max.setValue(as_int("normal_max_days", 40))
        self.attention_min.setValue(as_int("attention_min_days", 41))
        self.attention_max.setValue(as_int("attention_max_days", 49))
        self.urgent_min.setValue(as_int("urgent_min_days", 50))
        self.urgent_max.setValue(as_int("urgent_max_days", 59))
        self.critical_min.setValue(as_int("critical_min_days", 60))

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
