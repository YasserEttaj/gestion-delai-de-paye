from __future__ import annotations

from PyQt6.QtCore import QRectF, QSettings, Qt
from PyQt6.QtGui import QBrush, QColor, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.auth.session import AuthSession
from app.main_window import MainWindow
from app.services.auth_service import AuthService
from app.services.settings_service import SettingsService
from app.services.translation_service import TranslationService
from app.styles.themes import apply_theme
from app.ui.icons import MOON_ICON, SUN_ICON
from app.ui.widgets.modern_button import ModernButton
from config import APP_ABBREVIATION, APP_ICON_PATH, APP_NAME, AUTH_IMAGE_PATH, COMPANY_NAME


class CoverImagePanel(QFrame):
    def __init__(self, image_path, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("AuthImagePanel")
        self.pixmap = QPixmap(str(image_path)) if image_path.exists() else QPixmap()
        self.caption = "Gestion sécurisée des fournisseurs, factures et paiements."
        self.setMinimumWidth(430)

    def set_caption(self, text: str) -> None:
        self.caption = text
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 24, 24)
        painter.setClipPath(path)

        if not self.pixmap.isNull():
            scaled = self.pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = int((self.width() - scaled.width()) / 2)
            y = int((self.height() - scaled.height()) / 2)
            painter.drawPixmap(x, y, scaled)
        else:
            painter.fillRect(rect, QColor("#DDEAF8"))

        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(15, 23, 42, 25))
        gradient.setColorAt(0.58, QColor(15, 23, 42, 12))
        gradient.setColorAt(1, QColor(15, 23, 42, 188))
        painter.fillRect(rect, QBrush(gradient))

        painter.setClipping(False)
        painter.setPen(QPen(QColor(255, 255, 255, 70), 1))
        painter.drawRoundedRect(rect, 24, 24)

        painter.setPen(QColor("#FFFFFF"))
        title_rect = QRectF(32, self.height() - 132, self.width() - 64, 46)
        font = painter.font()
        font.setPointSize(24)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, COMPANY_NAME)

        painter.setPen(QColor(226, 232, 240, 230))
        font.setPointSize(11)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(
            QRectF(32, self.height() - 86, self.width() - 64, 54),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            self.caption,
        )


class LoginWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.settings = SettingsService.all()
        self.local_settings = QSettings(COMPANY_NAME, APP_ABBREVIATION)
        self.translator = TranslationService(self.settings.get("default_language", "fr"))
        self.theme = self.settings.get("default_theme", "dark")
        self.setObjectName("LoginRoot")
        self.setWindowTitle(APP_NAME)
        if APP_ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(APP_ICON_PATH)))
        self.setMinimumSize(1040, 700)
        self.resize(1120, 720)
        apply_theme(QApplication.instance(), self.theme)
        self._build_ui()
        self._retranslate()
        self._center()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(52, 42, 52, 42)
        root.setSpacing(34)

        self.image_panel = CoverImagePanel(AUTH_IMAGE_PATH)
        root.addWidget(self.image_panel, 1)

        self.card = QFrame()
        self.card.setObjectName("AuthCard")
        self.card.setProperty("card", True)
        self.card.setMinimumWidth(440)
        self.card.setMaximumWidth(500)
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(34)
        shadow.setOffset(0, 18)
        shadow.setColor(QColor(0, 0, 0, 85))
        self.card.setGraphicsEffect(shadow)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(34, 32, 34, 28)
        card_layout.setSpacing(14)

        self.eyebrow = QLabel("Secure access")
        self.eyebrow.setObjectName("AuthEyebrow")
        self.title = QLabel()
        self.title.setObjectName("AuthTitle")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("AuthSubtitle")
        self.subtitle.setWordWrap(True)
        card_layout.addWidget(self.eyebrow)
        card_layout.addWidget(self.title)
        card_layout.addWidget(self.subtitle)

        tabs = QHBoxLayout()
        tabs.setSpacing(8)
        self.login_tab = ModernButton("", "secondary")
        self.login_tab.clicked.connect(lambda: self.set_mode("login"))
        self.register_tab = ModernButton("", "secondary")
        self.register_tab.clicked.connect(lambda: self.set_mode("register"))
        tabs.addWidget(self.login_tab)
        tabs.addWidget(self.register_tab)
        card_layout.addLayout(tabs)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_login_form())
        self.stack.addWidget(self._build_register_form())
        card_layout.addWidget(self.stack, 1)

        bottom = QHBoxLayout()
        self.language = QComboBox()
        self.language.addItem("FR", "fr")
        self.language.addItem("EN", "en")
        self.language.setCurrentIndex(max(self.language.findData(self.translator.language), 0))
        self.language.currentIndexChanged.connect(self.change_language)
        self.theme_button = ModernButton("", "secondary")
        self.theme_button.clicked.connect(self.toggle_theme)
        bottom.addWidget(self.language)
        bottom.addStretch(1)
        bottom.addWidget(self.theme_button)
        card_layout.addLayout(bottom)

        root.addWidget(self.card, 0, Qt.AlignmentFlag.AlignVCenter)
        remembered = self.local_settings.value("remembered_username", "", str)
        if remembered:
            self.login_identifier.setText(remembered)
            self.remember.setChecked(True)
        self.set_mode("login")

    def _build_login_form(self) -> QWidget:
        form = QWidget()
        layout = QVBoxLayout(form)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(12)

        self.login_identifier = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_identifier.returnPressed.connect(self.login)
        self.login_password.returnPressed.connect(self.login)
        layout.addWidget(self.login_identifier)
        layout.addLayout(self._password_row(self.login_password, "login"))

        options = QHBoxLayout()
        self.remember = QCheckBox()
        self.forgot_button = ModernButton("", "ghost")
        self.forgot_button.clicked.connect(self.forgot_password)
        options.addWidget(self.remember)
        options.addStretch(1)
        options.addWidget(self.forgot_button)
        layout.addLayout(options)

        self.login_message = QLabel("")
        self.login_message.setObjectName("AuthMessage")
        self.login_message.setWordWrap(True)
        layout.addWidget(self.login_message)

        self.login_button = ModernButton("", "primary")
        self.login_button.setMinimumHeight(46)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        layout.addStretch(1)
        return form

    def _build_register_form(self) -> QWidget:
        form = QWidget()
        layout = QVBoxLayout(form)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(10)

        self.register_full_name = QLineEdit()
        self.register_username = QLineEdit()
        self.register_email = QLineEdit()
        self.register_phone = QLineEdit()
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_confirm = QLineEdit()
        self.register_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_confirm.returnPressed.connect(self.register)

        layout.addWidget(self.register_full_name)
        layout.addWidget(self.register_username)
        layout.addWidget(self.register_email)
        layout.addWidget(self.register_phone)
        layout.addLayout(self._password_row(self.register_password, "register"))
        layout.addLayout(self._password_row(self.register_confirm, "confirm"))

        self.register_message = QLabel("")
        self.register_message.setObjectName("AuthMessage")
        self.register_message.setWordWrap(True)
        layout.addWidget(self.register_message)

        self.register_button = ModernButton("", "primary")
        self.register_button.setMinimumHeight(46)
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)
        return form

    def _password_row(self, field: QLineEdit, key: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        button = ModernButton("", "ghost")
        button.setMinimumWidth(86)
        button.clicked.connect(lambda _=False, target=field, toggle=button: self.toggle_password(target, toggle))
        setattr(self, f"{key}_password_toggle", button)
        row.addWidget(field, 1)
        row.addWidget(button)
        return row

    def _center(self) -> None:
        screen = self.screen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "image_panel"):
            self.image_panel.setVisible(self.width() >= 980)

    def set_mode(self, mode: str) -> None:
        self.stack.setCurrentIndex(0 if mode == "login" else 1)
        self.login_tab.setProperty("active", mode == "login")
        self.register_tab.setProperty("active", mode == "register")
        for button in (self.login_tab, self.register_tab):
            button.style().unpolish(button)
            button.style().polish(button)
        self._update_header(mode)

    def _update_header(self, mode: str) -> None:
        if mode == "register":
            self.title.setText(self.translator.text("create_account"))
            self.subtitle.setText(self.translator.text("register_subtitle"))
        else:
            self.title.setText(self.translator.tr("login"))
            self.subtitle.setText(self.translator.text("login_subtitle"))

    def _set_message(self, label: QLabel, text: str, success: bool = False) -> None:
        label.setText(text)
        label.setProperty("success", success)
        label.style().unpolish(label)
        label.style().polish(label)

    def _retranslate(self) -> None:
        tr = self.translator.tr
        text = self.translator.text
        self.image_panel.set_caption(text("auth_cover_caption"))
        self.eyebrow.setText(text("secure_access"))
        self.login_identifier.setPlaceholderText(tr("username"))
        self.login_password.setPlaceholderText(tr("password"))
        self.register_full_name.setPlaceholderText(text("full_name_required"))
        self.register_username.setPlaceholderText(text("username_required"))
        self.register_email.setPlaceholderText(text("email_required"))
        self.register_phone.setPlaceholderText(text("phone_optional"))
        self.register_password.setPlaceholderText(text("password_required"))
        self.register_confirm.setPlaceholderText(text("confirm_password"))
        self.remember.setText(tr("remember_me"))
        self.forgot_button.setText(text("forgot_password"))
        self.login_button.setText(tr("login"))
        self.register_button.setText(text("create_account"))
        self.login_tab.setText(tr("login"))
        self.register_tab.setText(text("create_account"))
        self.theme_button.setText(text("dark_mode") if self.theme == "light" else text("light_mode"))
        self.theme_button.set_app_icon(MOON_ICON if self.theme == "light" else SUN_ICON)
        for field, button in [
            (self.login_password, self.login_password_toggle),
            (self.register_password, self.register_password_toggle),
            (self.register_confirm, self.confirm_password_toggle),
        ]:
            button.setText(tr("show_password") if field.echoMode() == QLineEdit.EchoMode.Password else tr("hide_password"))
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._update_header("register" if self.stack.currentIndex() == 1 else "login")

    def toggle_password(self, field: QLineEdit, button: ModernButton) -> None:
        if field.echoMode() == QLineEdit.EchoMode.Password:
            field.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
        button.setText(
            self.translator.tr("show_password")
            if field.echoMode() == QLineEdit.EchoMode.Password
            else self.translator.tr("hide_password")
        )

    def change_language(self) -> None:
        self.translator.set_language(self.language.currentData())
        self._retranslate()

    def toggle_theme(self) -> None:
        self.theme = "light" if self.theme == "dark" else "dark"
        apply_theme(QApplication.instance(), self.theme)
        self._retranslate()

    def forgot_password(self) -> None:
        QMessageBox.information(
            self,
            self.translator.text("forgot_password_title"),
            self.translator.text("forgot_password_message"),
        )

    def login(self) -> None:
        self._set_message(self.login_message, "")
        user, error, default_password = AuthService.login(self.login_identifier.text(), self.login_password.text())
        if error:
            self._set_message(self.login_message, error)
            return
        if not user:
            self._set_message(self.login_message, self.translator.text("login_failed"))
            return
        AuthSession.start(user)
        if self.remember.isChecked():
            self.local_settings.setValue("remembered_username", self.login_identifier.text().strip())
        else:
            self.local_settings.remove("remembered_username")
        if default_password:
            QMessageBox.warning(
                self,
                self.translator.text("security"),
                self.translator.text("default_password_warning"),
            )
        self.main_window = MainWindow(user, self.theme, self.translator.language)
        self.main_window.show()
        self.close()

    def register(self) -> None:
        self._set_message(self.register_message, "")
        try:
            user = AuthService.register_user(
                {
                    "full_name": self.register_full_name.text(),
                    "username": self.register_username.text(),
                    "email": self.register_email.text(),
                    "phone": self.register_phone.text(),
                    "password": self.register_password.text(),
                    "confirm_password": self.register_confirm.text(),
                }
            )
        except ValueError as exc:
            self._set_message(self.register_message, str(exc))
            return
        except Exception:
            self._set_message(self.register_message, "Impossible de créer le compte pour le moment.")
            return

        self.login_identifier.setText(user.username)
        self.login_password.clear()
        for field in (
            self.register_full_name,
            self.register_username,
            self.register_email,
            self.register_phone,
            self.register_password,
            self.register_confirm,
        ):
            field.clear()
        self.set_mode("login")
        self._set_message(self.login_message, self.translator.text("account_created"), success=True)
