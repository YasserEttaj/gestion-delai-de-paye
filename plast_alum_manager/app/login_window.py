from __future__ import annotations

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from app.main_window import MainWindow
from app.services.auth_service import AuthService
from app.services.settings_service import SettingsService
from app.services.translation_service import TranslationService
from app.styles.themes import apply_theme
from app.ui.widgets.modern_button import ModernButton
from config import APP_ICON_PATH, APP_NAME, COMPANY_NAME, LOGO_PATH, MIN_HEIGHT, MIN_WIDTH


class LoginWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.settings = SettingsService.all()
        self.local_settings = QSettings("PLAST ALUM", "Paiements Fournisseurs")
        self.translator = TranslationService(self.settings.get("default_language", "fr"))
        self.theme = self.settings.get("default_theme", "dark")
        self.setObjectName("LoginRoot")
        self.setWindowTitle(APP_NAME)
        if APP_ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(APP_ICON_PATH)))
        self.setMinimumSize(920, 620)
        apply_theme(QApplication.instance(), self.theme)
        self._build_ui()
        self._retranslate()
        self._center()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(90, 58, 90, 58)
        root.setSpacing(48)

        brand = QVBoxLayout()
        brand.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        logo = QLabel(COMPANY_NAME)
        if LOGO_PATH.exists():
            logo.setPixmap(QPixmap(str(LOGO_PATH)).scaledToWidth(360, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setStyleSheet("font-size:42px; font-weight:900; color:#2563EB;")
        subtitle = QLabel("Gestion professionnelle des paiements fournisseurs")
        subtitle.setProperty("muted", True)
        subtitle.setStyleSheet("font-size:18px;")
        brand.addWidget(logo)
        brand.addSpacing(34)
        brand.addWidget(subtitle)
        brand.addSpacing(30)
        value = QLabel("Factures • Délais • Alertes • Rapports • Sauvegardes")
        value.setProperty("muted", True)
        brand.addWidget(value)
        root.addLayout(brand, 1)

        card = QFrame()
        card.setObjectName("LoginCard")
        card.setProperty("card", True)
        card.setFixedSize(430, 500)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(36, 34, 36, 34)
        layout.setSpacing(16)
        self.title = QLabel()
        self.title.setProperty("heading", True)
        layout.addWidget(self.title)
        layout.addSpacing(20)

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.returnPressed.connect(self.login)
        self.username.returnPressed.connect(self.login)
        layout.addWidget(self.username)
        layout.addWidget(self.password)

        options = QHBoxLayout()
        self.remember = QCheckBox()
        self.show_password = ModernButton("", "ghost")
        self.show_password.clicked.connect(self.toggle_password)
        options.addWidget(self.remember)
        options.addStretch(1)
        options.addWidget(self.show_password)
        layout.addLayout(options)

        self.error = QLabel("")
        self.error.setStyleSheet("color:#EF4444; font-weight:700;")
        self.error.setWordWrap(True)
        layout.addWidget(self.error)
        layout.addStretch(1)

        self.login_button = ModernButton("", "primary")
        self.login_button.setMinimumHeight(44)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        bottom = QHBoxLayout()
        self.language = QComboBox()
        self.language.addItem("FR", "fr")
        self.language.addItem("AR", "ar")
        self.language.setCurrentIndex(max(self.language.findData(self.translator.language), 0))
        self.language.currentIndexChanged.connect(self.change_language)
        self.theme_button = ModernButton("Mode clair" if self.theme == "dark" else "Mode sombre", "secondary")
        self.theme_button.clicked.connect(self.toggle_theme)
        bottom.addWidget(self.language)
        bottom.addStretch(1)
        bottom.addWidget(self.theme_button)
        layout.addLayout(bottom)
        root.addWidget(card, 0, Qt.AlignmentFlag.AlignVCenter)
        remembered = self.local_settings.value("remembered_username", "", str)
        if remembered:
            self.username.setText(remembered)
            self.remember.setChecked(True)

    def _center(self) -> None:
        screen = self.screen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

    def _retranslate(self) -> None:
        tr = self.translator.tr
        self.title.setText(tr("login"))
        self.username.setPlaceholderText(tr("username"))
        self.password.setPlaceholderText(tr("password"))
        self.remember.setText(tr("remember_me"))
        self.show_password.setText(tr("show_password") if self.password.echoMode() == QLineEdit.EchoMode.Password else tr("hide_password"))
        self.login_button.setText(tr("login"))
        direction = Qt.LayoutDirection.RightToLeft if self.translator.language == "ar" else Qt.LayoutDirection.LeftToRight
        self.setLayoutDirection(direction)

    def toggle_password(self) -> None:
        if self.password.echoMode() == QLineEdit.EchoMode.Password:
            self.password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self._retranslate()

    def change_language(self) -> None:
        self.translator.set_language(self.language.currentData())
        self._retranslate()

    def toggle_theme(self) -> None:
        self.theme = "light" if self.theme == "dark" else "dark"
        self.theme_button.setText("Mode sombre" if self.theme == "light" else "Mode clair")
        apply_theme(QApplication.instance(), self.theme)

    def login(self) -> None:
        self.error.setText("")
        user, error, default_password = AuthService.login(self.username.text(), self.password.text())
        if error:
            self.error.setText(error)
            return
        if not user:
            self.error.setText("Connexion impossible.")
            return
        if self.remember.isChecked():
            self.local_settings.setValue("remembered_username", self.username.text().strip())
        else:
            self.local_settings.remove("remembered_username")
        if default_password:
            QMessageBox.warning(
                self,
                "Sécurité",
                "Le compte admin utilise encore le mot de passe par défaut admin123. Changez-le depuis la page Utilisateurs.",
            )
        self.main_window = MainWindow(user, self.theme, self.translator.language)
        self.main_window.show()
        self.close()
