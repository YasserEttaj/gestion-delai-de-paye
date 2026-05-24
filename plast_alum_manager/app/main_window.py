from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QMainWindow, QMenu, QMessageBox, QStackedWidget, QStatusBar, QVBoxLayout, QWidget

from app.auth.session import AuthSession
from app.services.auth_service import AuthService
from app.services.backup_service import BackupService
from app.services.convention_service import ConventionService
from app.services.invoice_service import InvoiceService
from app.services.settings_service import SettingsService
from app.services.translation_service import TranslationService
from app.styles.themes import apply_theme
from app.ui.pages.activity_logs_page import ActivityLogsPage
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.conventions_page import ConventionsPage
from app.ui.pages.import_excel_page import ImportExcelPage
from app.ui.pages.invoices_page import InvoicesPage
from app.ui.pages.reports_page import ReportsPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.pages.suppliers_page import SuppliersPage
from app.ui.pages.users_page import UsersPage
from app.ui.widgets.modern_button import ModernButton
from app.ui.widgets.sidebar import Sidebar
from app.ui.widgets.topbar import Topbar
from config import APP_ICON_PATH, APP_NAME, MIN_HEIGHT, MIN_WIDTH, ROLE_ADMIN


class MainWindow(QMainWindow):
    TITLES = {
        "dashboard": "Tableau de bord",
        "suppliers": "Fournisseurs",
        "invoices": "Factures",
        "conventions": "Deadlines / Conventions",
        "reports": "Rapports",
        "import_excel": "Import Excel",
        "users": "Utilisateurs",
        "settings": "Paramètres",
        "activity_logs": "Journal d'activité",
    }
    TITLE_KEYS = {
        "dashboard": "dashboard_title",
        "suppliers": "suppliers_title",
        "invoices": "invoices_title",
        "invoice_form": "add_invoice",
        "conventions": "conventions_title",
        "reports": "reports_title",
        "import_excel": "import_excel_title",
        "users": "users_title",
        "settings": "settings_title",
        "activity_logs": "activity_logs_title",
    }

    def __init__(self, user, theme: str = "dark", language: str = "fr") -> None:
        super().__init__()
        self.user = user
        AuthSession.start(user)
        self.theme = theme
        self.translator = TranslationService(language)
        self.current_page = "dashboard"
        self.setWindowTitle(APP_NAME)
        if APP_ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(APP_ICON_PATH)))
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.pages: dict[str, QWidget] = {}
        self.allowed_pages = self._allowed_pages()
        self._build_ui()
        self.navigate("dashboard")
        self.refresh_notifications()
        self._center()

    def _allowed_pages(self) -> set[str]:
        pages = {"dashboard", "suppliers", "invoices", "reports"}
        if self.user.can_edit:
            pages.add("invoice_form")
        if self.user.can_import_export:
            pages.add("import_excel")
        if getattr(self.user, "can_manage_conventions", False):
            pages.add("conventions")
        if self.user.role == ROLE_ADMIN:
            pages.update({"users", "settings", "activity_logs"})
        return pages

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("AppRoot")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar(self.allowed_pages)
        self.sidebar.setFixedWidth(250)
        self.sidebar.page_requested.connect(self.navigate)
        self.sidebar.logout_requested.connect(self.logout)
        layout.addWidget(self.sidebar)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        self.topbar = Topbar(self.user.full_name)
        self.topbar.set_theme(self.theme)
        self.topbar.set_language(self.translator.language)
        self.topbar.set_ui_language(self.translator.language)
        self.topbar.search_changed.connect(self.global_search)
        self.topbar.theme_changed.connect(self.change_theme)
        self.topbar.language_changed.connect(self.change_language)
        self.topbar.notifications_requested.connect(self.show_notifications)
        right.addWidget(self.topbar)

        self.stack = QStackedWidget()
        right.addWidget(self.stack, 1)
        layout.addLayout(right, 1)

        self.pages["dashboard"] = DashboardPage(self.user)
        self.pages["dashboard"].quick_action_requested.connect(self.navigate)
        self.pages["suppliers"] = SuppliersPage(self.user)
        self.pages["suppliers"].supplier_invoices_requested.connect(self.open_supplier_invoices)
        self.pages["invoices"] = InvoicesPage(self.user)
        if "conventions" in self.allowed_pages:
            self.pages["conventions"] = ConventionsPage(self.user)
        self.pages["reports"] = ReportsPage(self.user)
        if "import_excel" in self.allowed_pages:
            self.pages["import_excel"] = ImportExcelPage(self.user)
        if "users" in self.allowed_pages:
            self.pages["users"] = UsersPage(self.user)
        if "settings" in self.allowed_pages:
            self.pages["settings"] = SettingsPage(self.user)
        if "activity_logs" in self.allowed_pages:
            self.pages["activity_logs"] = ActivityLogsPage(self.user)
        for key, page in self.pages.items():
            self.stack.addWidget(page)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage(self.translator.text("ready"))

    def _center(self) -> None:
        screen = self.screen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

    def navigate(self, page: str) -> None:
        if page == "suppliers:add":
            if not self.user.can_edit:
                return
            self.navigate("suppliers")
            self.pages["suppliers"].add_supplier()
            return
        if page == "invoice_form":
            if not self.user.can_edit:
                return
            self.navigate("invoices")
            self.pages["invoices"].add_invoice()
            return
        if page == "conventions" and not getattr(self.user, "can_manage_conventions", False):
            QMessageBox.warning(
                self,
                self.translator.text("access_denied"),
                self.translator.text("authorized_users_only"),
            )
            return
        if page in {"users", "settings", "activity_logs"} and not self.user.can_manage_users:
            QMessageBox.warning(
                self,
                self.translator.text("access_denied"),
                self.translator.text("admins_only"),
            )
            return
        if page not in self.pages:
            return
        self.current_page = page
        self.stack.setCurrentWidget(self.pages[page])
        self.sidebar.set_active(page)
        self.topbar.set_title(self._translated_title(page))
        refresh = getattr(self.pages[page], "refresh", None)
        if callable(refresh):
            refresh()
        self.refresh_notifications()
        self.retranslate_ui()

    def open_supplier_invoices(self, supplier_id: int) -> None:
        self.navigate("invoices")
        self.pages["invoices"].set_supplier_filter(supplier_id)

    def global_search(self, text: str) -> None:
        page = self.stack.currentWidget()
        if hasattr(page, "search"):
            page.search.setText(text)

    def change_theme(self, theme: str) -> None:
        from PyQt6.QtWidgets import QApplication

        self.theme = theme
        apply_theme(QApplication.instance(), theme)
        for button in self.findChildren(ModernButton):
            button.refresh_icon_theme()
        self.topbar.set_theme(theme)
        self.sidebar.refresh_icons()
        SettingsService.set_many({"default_theme": theme}, self.user.id)
        page = self.stack.currentWidget()
        refresh = getattr(page, "refresh", None)
        if callable(refresh):
            refresh()
        self.retranslate_ui()

    def change_language(self, language: str) -> None:
        self.translator.set_language(language)
        SettingsService.set_many({"default_language": self.translator.language}, self.user.id)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.retranslate_ui()
        QMessageBox.information(
            self,
            self.translator.text("settings_default_language"),
            self.translator.text("language_updated"),
        )

    def _translated_title(self, page: str) -> str:
        return self.translator.text(self.TITLE_KEYS.get(page, page), self.TITLES.get(page, page))

    def retranslate_ui(self) -> None:
        self.topbar.set_language(self.translator.language)
        self.topbar.set_ui_language(self.translator.language)
        self.topbar.set_title(self._translated_title(getattr(self, "current_page", "dashboard")))
        self.translator.apply_to_widget(self.sidebar)
        for page in self.pages.values():
            self.translator.apply_to_widget(page)
        if self.statusBar():
            self.statusBar().showMessage(self.translator.text("ready"))

    def refresh_notifications(self) -> None:
        self.notifications = InvoiceService.notifications()
        if getattr(self.user, "can_manage_conventions", False):
            self.notifications.extend(ConventionService.notifications())
        self.topbar.set_notification_count(len(self.notifications))

    def show_notifications(self) -> None:
        self.refresh_notifications()
        menu = QMenu(self)
        if not self.notifications:
            menu.addAction(self.translator.text("notifications_none"))
        for note in self.notifications[:20]:
            action = menu.addAction(f"{note['title']} - {note['message']}")
            invoice_id = note.get("invoice_id")
            if invoice_id:
                action.triggered.connect(lambda _=False, iid=invoice_id: self._open_invoice_from_notification(iid))
            convention_id = note.get("convention_id")
            if convention_id:
                action.triggered.connect(lambda _=False, cid=convention_id: self._open_convention_from_notification(cid))
        menu.exec(self.topbar.notification_button.mapToGlobal(self.topbar.notification_button.rect().bottomLeft()))

    def _open_invoice_from_notification(self, invoice_id: int) -> None:
        self.navigate("invoices")
        self.pages["invoices"].view_invoice(invoice_id)

    def _open_convention_from_notification(self, convention_id: int) -> None:
        self.navigate("conventions")

    def logout(self) -> None:
        AuthService.logout(self.user.id)
        AuthSession.clear()
        from app.login_window import LoginWindow

        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def closeEvent(self, event) -> None:
        settings = SettingsService.all()
        if settings.get("auto_backup_on_close", "true") == "true":
            try:
                BackupService.create_backup(self.user.id, int(settings.get("auto_backup_keep", 10)))
            except Exception:
                pass
        super().closeEvent(event)
