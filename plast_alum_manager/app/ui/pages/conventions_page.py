from __future__ import annotations

from datetime import date

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QAbstractSpinBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.convention_model import Convention
from app.services.convention_service import (
    CONVENTION_STATUS_ACTIVE,
    CONVENTION_STATUS_COLORS,
    CONVENTION_STATUS_COMPLETED,
    CONVENTION_STATUS_EXPIRED,
    CONVENTION_STATUS_LABELS,
    CONVENTION_STATUS_WARNING,
    DEADLINE_OPTIONS,
    ConventionService,
)
from app.ui.widgets.confirm_dialog import ConfirmDialog
from app.ui.widgets.modern_button import ModernButton
from app.ui.widgets.modern_table import ModernTable
from app.ui.widgets.stat_card import StatCard


def _qdate_from_text(value: str | None) -> QDate:
    parsed = ConventionService.parse_date(value)
    if not parsed:
        parsed = date.today()
    return QDate(parsed.year, parsed.month, parsed.day)


class ConventionDialog(QDialog):
    def __init__(self, convention: Convention | None = None, parent=None) -> None:
        super().__init__(parent)
        self.convention = convention
        self.setWindowTitle("Convention")
        self.setMinimumWidth(620)
        layout = QVBoxLayout(self)

        title = QLabel("Échéance de convention")
        title.setProperty("heading", True)
        layout.addWidget(title)
        hint = QLabel("Délais configurables selon le type de convention et le dossier de l'entreprise.")
        hint.setProperty("muted", True)
        hint.setWordWrap(True)
        layout.addWidget(hint)

        form = QFormLayout()
        form.setVerticalSpacing(12)
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Nom de la société *")
        self.convention_number = QLineEdit()
        self.convention_number.setPlaceholderText("Numéro de convention *")
        self.convention_type = QComboBox()
        self.convention_type.setEditable(True)
        self.convention_type.addItems(["Convention commerciale", "Convention fiscale", "Contrat fournisseur", "Accord cadre", "Autre"])
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.deadline_type = QComboBox()
        for days in DEADLINE_OPTIONS:
            self.deadline_type.addItem(f"{days} jours", days)
        self.deadline_type.addItem("Personnalisé", "custom")
        self.deadline_type.currentIndexChanged.connect(self._sync_deadline_type)
        self.deadline_days = QSpinBox()
        self.deadline_days.setRange(1, 3650)
        self.deadline_days.setValue(60)
        self.deadline_days.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.notes = QTextEdit()
        self.notes.setFixedHeight(92)

        form.addRow("Société *", self.company_name)
        form.addRow("Numéro *", self.convention_number)
        form.addRow("Type *", self.convention_type)
        form.addRow("Date de début *", self.start_date)
        form.addRow("Délai", self.deadline_type)
        form.addRow("Jours", self.deadline_days)
        form.addRow("Notes", self.notes)
        layout.addLayout(form)

        self.preview = QLabel()
        self.preview.setProperty("muted", True)
        layout.addWidget(self.preview)

        self.error = QLabel("")
        self.error.setStyleSheet("color:#EF4444; font-weight:700;")
        self.error.setWordWrap(True)
        layout.addWidget(self.error)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Enregistrer")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annuler")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.start_date.dateChanged.connect(self._refresh_preview)
        self.deadline_days.valueChanged.connect(self._refresh_preview)
        if convention:
            self._load(convention)
        self._sync_deadline_type()
        self._refresh_preview()

    def _load(self, convention: Convention) -> None:
        self.company_name.setText(convention.company_name or "")
        self.convention_number.setText(convention.convention_number or "")
        index = self.convention_type.findText(convention.convention_type or "")
        if index >= 0:
            self.convention_type.setCurrentIndex(index)
        else:
            self.convention_type.setEditText(convention.convention_type or "")
        self.start_date.setDate(_qdate_from_text(convention.start_date))
        deadline_index = self.deadline_type.findData(convention.deadline_days)
        if deadline_index >= 0:
            self.deadline_type.setCurrentIndex(deadline_index)
        else:
            self.deadline_type.setCurrentIndex(self.deadline_type.findData("custom"))
        self.deadline_days.setValue(int(convention.deadline_days or 60))
        self.notes.setPlainText(convention.notes or "")

    def _sync_deadline_type(self) -> None:
        value = self.deadline_type.currentData()
        is_custom = value == "custom"
        self.deadline_days.setReadOnly(not is_custom)
        self.deadline_days.setEnabled(True)
        if not is_custom and value:
            self.deadline_days.setValue(int(value))
        self._refresh_preview()

    def _refresh_preview(self) -> None:
        try:
            result = ConventionService.calculate(self.start_date.date().toString("yyyy-MM-dd"), self.deadline_days.value())
            status = CONVENTION_STATUS_LABELS.get(result["status"], result["status"])
            self.preview.setText(f"Échéance calculée : {result['due_date']} • {result['remaining_days']} jour(s) • {status}")
        except ValueError as exc:
            self.preview.setText(str(exc))

    def accept(self) -> None:
        if not self.company_name.text().strip():
            self.error.setText("Le nom de la société est obligatoire.")
            return
        if not self.convention_number.text().strip():
            self.error.setText("Le numéro de convention est obligatoire.")
            return
        if not self.convention_type.currentText().strip():
            self.error.setText("Le type de convention est obligatoire.")
            return
        if self.deadline_days.value() <= 0:
            self.error.setText("Le délai doit être positif.")
            return
        try:
            ConventionService.calculate(self.start_date.date().toString("yyyy-MM-dd"), self.deadline_days.value())
        except ValueError as exc:
            self.error.setText(str(exc))
            return
        super().accept()

    def data(self) -> dict:
        return {
            "company_name": self.company_name.text().strip(),
            "convention_number": self.convention_number.text().strip(),
            "convention_type": self.convention_type.currentText().strip(),
            "start_date": self.start_date.date().toString("yyyy-MM-dd"),
            "deadline_days": int(self.deadline_days.value()),
            "notes": self.notes.toPlainText().strip() or None,
        }


class ConventionsPage(QWidget):
    def __init__(self, user, parent=None) -> None:
        super().__init__(parent)
        self.user = user
        self.rows: list[Convention] = []
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        top = QHBoxLayout()
        title = QLabel("Deadlines / Conventions")
        title.setProperty("heading", True)
        top.addWidget(title)
        top.addStretch(1)
        self.recalculate_button = ModernButton("Recalculer", "secondary")
        self.recalculate_button.clicked.connect(self.recalculate)
        self.export_excel_button = ModernButton("Export Excel", "success")
        self.export_excel_button.clicked.connect(self.export_excel)
        self.export_pdf_button = ModernButton("Export PDF", "danger")
        self.export_pdf_button.clicked.connect(self.export_pdf)
        self.add_button = ModernButton("Ajouter convention", "primary")
        self.add_button.clicked.connect(self.add_convention)
        for button in (self.recalculate_button, self.export_excel_button, self.export_pdf_button, self.add_button):
            top.addWidget(button)
        root.addLayout(top)

        notice = QLabel("Les délais sont configurables par dossier. Ce module ne remplace pas un avis juridique ou fiscal.")
        notice.setProperty("muted", True)
        notice.setWordWrap(True)
        root.addWidget(notice)

        cards = QGridLayout()
        cards.setHorizontalSpacing(14)
        self.cards = {
            "total": StatCard("Total conventions", "0", "", "C", "#2563EB"),
            "active": StatCard("Active", "0", "", "✓", "#22C55E"),
            "warning": StatCard("Near deadline", "0", "≤ 15 jours", "!", "#F59E0B"),
            "expired": StatCard("Expired", "0", "", "×", "#DC2626"),
            "completed": StatCard("Completed", "0", "", "✓", "#64748B"),
        }
        for idx, card in enumerate(self.cards.values()):
            cards.addWidget(card, 0, idx)
        root.addLayout(cards)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Recherche société ou numéro de convention")
        self.search.textChanged.connect(self.refresh)
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous statuts", "")
        for status in (CONVENTION_STATUS_ACTIVE, CONVENTION_STATUS_WARNING, CONVENTION_STATUS_EXPIRED, CONVENTION_STATUS_COMPLETED):
            self.status_filter.addItem(CONVENTION_STATUS_LABELS[status], status)
        self.status_filter.currentIndexChanged.connect(self.refresh)
        self.deadline_filter = QComboBox()
        self.deadline_filter.addItem("Tous délais", "")
        for days in DEADLINE_OPTIONS:
            self.deadline_filter.addItem(f"{days} jours", days)
        self.deadline_filter.addItem("Personnalisé", "custom")
        self.deadline_filter.currentIndexChanged.connect(self.refresh)
        filters.addWidget(self.search, 2)
        filters.addWidget(self.status_filter)
        filters.addWidget(self.deadline_filter)
        root.addLayout(filters)

        self.table = ModernTable()
        self.table.set_headers(["Company", "Convention number", "Type", "Start date", "Deadline", "Due date", "Remaining days", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table, 1)
        self.refresh()

    def _filters(self) -> dict:
        deadline = self.deadline_filter.currentData()
        filters = {
            "search": self.search.text(),
            "status": self.status_filter.currentData(),
        }
        if deadline == "custom":
            filters["custom_deadline"] = True
        elif deadline:
            filters["deadline_days"] = deadline
        return filters

    def refresh(self) -> None:
        filters = self._filters()
        rows = ConventionService.list_conventions(filters)
        if filters.get("custom_deadline"):
            rows = [row for row in rows if row.deadline_days not in DEADLINE_OPTIONS]
        self.rows = rows
        self._refresh_cards()
        self._render_table()

    def _refresh_cards(self) -> None:
        stats = ConventionService.stats()
        self.cards["total"].set_value(str(stats["total"]))
        self.cards["active"].set_value(str(stats["active"]))
        self.cards["warning"].set_value(str(stats["warning"]))
        self.cards["expired"].set_value(str(stats["expired"]))
        self.cards["completed"].set_value(str(stats["completed"]))

    def _render_table(self) -> None:
        self.table.clearSpans()
        if not self.rows:
            self.table.show_empty("Aucune convention trouvée.", 9)
            return
        self.table.setRowCount(len(self.rows))
        for row_idx, convention in enumerate(self.rows):
            values = [
                convention.company_name,
                convention.convention_number,
                convention.convention_type,
                convention.start_date,
                f"{convention.deadline_days} jours",
                convention.due_date,
                convention.remaining_days,
            ]
            for col, value in enumerate(values):
                self.table.set_text_item(row_idx, col, value, align_right=col in {4, 6})
            self.table.setCellWidget(
                row_idx,
                7,
                self.table.badge(
                    CONVENTION_STATUS_LABELS.get(convention.status, convention.status),
                    CONVENTION_STATUS_COLORS.get(convention.status, "#64748B"),
                ),
            )
            actions = QWidget()
            h = QHBoxLayout(actions)
            h.setContentsMargins(0, 0, 0, 0)
            edit = ModernButton("Éditer", "secondary")
            edit.clicked.connect(lambda _=False, cid=convention.id: self.edit_convention(cid))
            complete = ModernButton("Terminer", "success")
            complete.setEnabled(convention.status != CONVENTION_STATUS_COMPLETED)
            complete.clicked.connect(lambda _=False, cid=convention.id: self.mark_completed(cid))
            delete = ModernButton("Supprimer", "danger")
            delete.clicked.connect(lambda _=False, cid=convention.id: self.delete_convention(cid))
            for button in (edit, complete, delete):
                h.addWidget(button)
            self.table.setCellWidget(row_idx, 8, actions)

    def add_convention(self) -> None:
        dialog = ConventionDialog(parent=self)
        if dialog.exec():
            try:
                ConventionService.create_convention(dialog.data(), self.user.id)
                self.refresh()
            except Exception as exc:
                ConfirmDialog.error(self, "Convention", str(exc))

    def edit_convention(self, convention_id: int) -> None:
        convention = next((row for row in self.rows if row.id == convention_id), None) or ConventionService.get_convention(convention_id)
        if not convention:
            return
        dialog = ConventionDialog(convention, self)
        if dialog.exec():
            try:
                ConventionService.update_convention(convention_id, dialog.data(), self.user.id)
                self.refresh()
            except Exception as exc:
                ConfirmDialog.error(self, "Convention", str(exc))

    def delete_convention(self, convention_id: int) -> None:
        if not ConfirmDialog.ask(self, "Confirmation", "Supprimer cette convention ?"):
            return
        try:
            ConventionService.delete_convention(convention_id, self.user.id)
            self.refresh()
        except Exception as exc:
            ConfirmDialog.error(self, "Convention", str(exc))

    def mark_completed(self, convention_id: int) -> None:
        try:
            ConventionService.mark_completed(convention_id, self.user.id)
            self.refresh()
        except Exception as exc:
            ConfirmDialog.error(self, "Convention", str(exc))

    def recalculate(self) -> None:
        try:
            count = ConventionService.recalculate_all(self.user.id)
            self.refresh()
            ConfirmDialog.info(self, "Recalcul", f"{count} convention(s) mise(s) à jour.")
        except Exception as exc:
            ConfirmDialog.error(self, "Recalcul", str(exc))

    def export_excel(self) -> None:
        try:
            path = ConventionService.export_excel(self.rows, self.user.id)
            ConfirmDialog.info(self, "Export Excel", f"Fichier créé: {path}")
        except Exception as exc:
            ConfirmDialog.error(self, "Export Excel", str(exc))

    def export_pdf(self) -> None:
        try:
            path = ConventionService.export_pdf(self.rows, self.user.full_name, self.user.id)
            ConfirmDialog.info(self, "Export PDF", f"Fichier créé: {path}")
        except Exception as exc:
            ConfirmDialog.error(self, "Export PDF", str(exc))
