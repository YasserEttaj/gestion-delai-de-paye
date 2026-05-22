from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from app.database.migrations import initialize_database
from app.database.seed import seed_defaults
from app.login_window import LoginWindow
from app.styles.themes import apply_theme
from config import APP_ICON_PATH, APP_NAME, ensure_directories


def bootstrap() -> None:
    ensure_directories()
    initialize_database()
    seed_defaults()


def main() -> int:
    bootstrap()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("PLAST ALUM")
    if APP_ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(APP_ICON_PATH)))
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings, True)
    apply_theme(app, "dark")
    window = LoginWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
