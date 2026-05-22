from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.services.activity_service import ActivityService
from app.services.backup_service import BackupService
from app.services.invoice_service import InvoiceService
from app.services.report_service import ReportService
from app.ui.widgets.modern_button import ModernButton
from app.ui.widgets.notification_card import NotificationCard
from app.ui.widgets.stat_card import StatCard


class DashboardPage(QWidget):
    quick_action_requested = pyqtSignal(str)

    def __init__(self, user, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("DashboardPage")
        self.user = user
        self.cards: dict[str, StatCard] = {}
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setObjectName("PageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        container.setObjectName("DashboardContainer")
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 28, 30, 30)
        layout.setSpacing(20)

        hero = QHBoxLayout()
        hero.setSpacing(14)
        greeting = QLabel(f"Bienvenue, {user.full_name}")
        greeting.setProperty("heading", True)
        hero.addWidget(greeting)
        hero.addStretch(1)
        backup = ModernButton("Sauvegarder base", "secondary")
        backup.clicked.connect(self._backup)
        hero.addWidget(backup)
        layout.addLayout(hero)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
        for column in range(3):
            grid.setColumnStretch(column, 1)
        card_defs = [
            ("total_suppliers", "Fournisseurs", "◇", "#2563EB"),
            ("total_invoices", "Factures", "▤", "#0EA5E9"),
            ("paid_count", "Payées", "✓", "#22C55E"),
            ("unpaid_count", "Non payées", "!", "#EF4444"),
            ("partial_count", "Partielles", "◐", "#F59E0B"),
            ("late_count", "En retard", "⏱", "#DC2626"),
            ("unpaid_amount", "Montant impayé", "MAD", "#7F1D1D"),
            ("paid_amount", "Montant payé", "MAD", "#16A34A"),
            ("critical_count", "Critiques +60j", "60", "#000000"),
        ]
        for idx, (key, title, icon, accent) in enumerate(card_defs):
            card = StatCard(title, "0", "", icon, accent)
            self.cards[key] = card
            grid.addWidget(card, idx // 3, idx % 3)
        layout.addLayout(grid)

        actions_panel = QFrame()
        actions_panel.setProperty("card", True)
        actions = QHBoxLayout(actions_panel)
        actions.setContentsMargins(14, 12, 14, 12)
        actions.setSpacing(12)
        for page, label in [
            ("suppliers:add", "Ajouter fournisseur"),
            ("invoice_form", "Ajouter facture"),
            ("import_excel", "Importer Excel"),
            ("reports", "Exporter rapport"),
        ]:
            button = ModernButton(label, "primary" if page == "invoice_form" else "secondary")
            button.clicked.connect(lambda _checked=False, target=page: self.quick_action_requested.emit(target))
            actions.addWidget(button)
        actions.addStretch(1)
        layout.addWidget(actions_panel)

        middle = QHBoxLayout()
        middle.setSpacing(18)
        self.chart_panel = QFrame()
        self.chart_panel.setProperty("card", True)
        self.chart_panel.setMinimumHeight(280)
        self.chart_layout = QVBoxLayout(self.chart_panel)
        self.chart_layout.setContentsMargins(16, 14, 16, 14)
        self.chart_layout.setSpacing(10)
        middle.addWidget(self.chart_panel, 2)

        self.alert_panel = QFrame()
        self.alert_panel.setProperty("card", True)
        self.alert_panel.setMinimumHeight(280)
        self.alert_layout = QVBoxLayout(self.alert_panel)
        self.alert_layout.setContentsMargins(16, 14, 16, 14)
        self.alert_layout.setSpacing(10)
        middle.addWidget(self.alert_panel, 1)
        layout.addLayout(middle)

        self.activity_panel = QFrame()
        self.activity_panel.setProperty("card", True)
        self.activity_panel.setMinimumHeight(185)
        self.activity_layout = QVBoxLayout(self.activity_panel)
        self.activity_layout.setContentsMargins(16, 14, 16, 14)
        self.activity_layout.setSpacing(6)
        layout.addWidget(self.activity_panel)
        root.addWidget(scroll)
        self.refresh()

    def _backup(self) -> None:
        path = BackupService.create_backup(self.user.id)
        self.refresh()
        from app.ui.widgets.toast_notification import ToastNotification

        ToastNotification.success(self, f"Sauvegarde créée: {path.name}")

    def refresh(self) -> None:
        stats = InvoiceService.dashboard_stats()
        money_keys = {"unpaid_amount", "paid_amount"}
        for key, card in self.cards.items():
            value = stats.get(key, 0)
            card.set_value(f"{value:,.2f} MAD" if key in money_keys else str(value))
        self._render_charts(stats)
        self._render_alerts(stats)
        self._render_activity()

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

    def _render_charts(self, stats: dict) -> None:
        self._clear_layout(self.chart_layout)
        title = QLabel("Analyse des paiements")
        title.setStyleSheet("font-size:16px; font-weight:800;")
        self.chart_layout.addWidget(title)
        try:
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure

            theme = QApplication.instance().property("theme") if QApplication.instance() else "dark"
            text_color = "#0F172A" if theme == "light" else "#E2E8F0"
            muted_color = "#475569" if theme == "light" else "#94A3B8"
            fig = Figure(figsize=(7, 2.65), facecolor="none")
            fig.patch.set_alpha(0)
            ax1 = fig.add_subplot(121)
            ax1.set_facecolor("none")
            status_values = [stats["paid_count"], stats["unpaid_count"], stats["partial_count"]]
            if sum(status_values):
                ax1.pie(
                    status_values,
                    labels=["Payées", "Non payées", "Partielles"],
                    colors=["#22C55E", "#EF4444", "#F59E0B"],
                    autopct="%1.0f%%",
                )
                ax1.set_title("Statuts", color=text_color, fontweight="bold")
            else:
                ax1.text(0.5, 0.5, "Aucune facture", ha="center", va="center", color=muted_color)
                ax1.axis("off")
            top = ReportService.top_suppliers_by_unpaid(5)
            ax2 = fig.add_subplot(122)
            ax2.set_facecolor("none")
            if top:
                ax2.barh([item[0][:18] for item in top], [item[1] for item in top], color="#2563EB")
                ax2.tick_params(colors=muted_color)
                ax2.set_title("Top impayés", color=text_color, fontweight="bold")
                for spine in ax2.spines.values():
                    spine.set_color("#334155" if theme != "light" else "#CBD5E1")
            else:
                ax2.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", color=muted_color)
                ax2.axis("off")
            fig.tight_layout()
            canvas = FigureCanvas(fig)
            canvas.setStyleSheet("background: transparent;")
            canvas.setMinimumHeight(210)
            self.chart_layout.addWidget(canvas)
        except Exception as exc:
            fallback = QLabel(f"Graphiques indisponibles: {exc}")
            fallback.setProperty("muted", True)
            self.chart_layout.addWidget(fallback)

    def _render_alerts(self, stats: dict) -> None:
        self._clear_layout(self.alert_layout)
        title = QLabel("Alertes prioritaires")
        title.setStyleSheet("font-size:16px; font-weight:800;")
        self.alert_layout.addWidget(title)
        rows = stats["critical_rows"] + stats["urgent_rows"]
        if not rows:
            self.alert_layout.addWidget(NotificationCard("Aucune alerte urgente", "Les délais sont sous contrôle.", "normal"))
        for row in rows[:8]:
            invoice = row["invoice"]
            self.alert_layout.addWidget(
                NotificationCard(
                    f"{row['deadline'].label} - {invoice.invoice_number}",
                    f"{row['supplier'].name} • {row['deadline'].days} jours • {row['outstanding_amount']:,.2f} MAD",
                    row["deadline"].category,
                )
            )
        self.alert_layout.addStretch(1)

    def _render_activity(self) -> None:
        self._clear_layout(self.activity_layout)
        title = QLabel("Activité récente")
        title.setStyleSheet("font-size:16px; font-weight:800;")
        self.activity_layout.addWidget(title)
        logs = ActivityService.list_logs(limit=6)
        if not logs:
            label = QLabel("Aucune activité enregistrée.")
            label.setProperty("muted", True)
            self.activity_layout.addWidget(label)
            self.activity_layout.addStretch(1)
            return
        for log in logs:
            user = log.user.username if log.user else "Système"
            details = log.details or ""
            if len(details) > 120:
                details = f"{details[:117]}..."
            label = QLabel(f"{log.created_at} • {user} • {log.action} • {details}")
            label.setProperty("muted", True)
            label.setWordWrap(False)
            self.activity_layout.addWidget(label)
        self.activity_layout.addStretch(1)
