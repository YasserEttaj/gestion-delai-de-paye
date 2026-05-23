from __future__ import annotations

from functools import lru_cache

from PyQt6.QtCore import QByteArray, QSize, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

from config import ASSETS_DIR


ICON_DIR = ASSETS_DIR / "icons"

COLOR_PRIMARY = "#2563EB"
COLOR_MUTED_DARK = "#CBD5E1"
COLOR_MUTED_LIGHT = "#334155"
COLOR_WHITE = "#FFFFFF"
COLOR_SUCCESS = "#22C55E"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"
COLOR_CRITICAL = "#7F1D1D"

DASHBOARD_ICON = "dashboard"
SUPPLIERS_ICON = "suppliers"
INVOICES_ICON = "invoices"
INVOICE_ADD_ICON = "invoice-add"
CONVENTIONS_ICON = "calendar-clock"
REPORTS_ICON = "reports"
IMPORT_ICON = "upload-cloud"
USERS_ICON = "users"
SETTINGS_ICON = "settings"
ACTIVITY_LOGS_ICON = "history"
LOGOUT_ICON = "log-out"

PAID_ICON = "check-circle"
UNPAID_ICON = "x-circle"
PARTIAL_ICON = "pie-chart"
WARNING_ICON = "alert-triangle"
CRITICAL_ICON = "triangle-alert"
LATE_ICON = "alarm-clock"
WALLET_ICON = "wallet"
WALLET_CHECK_ICON = "wallet-check"
CALENDAR_ALERT_ICON = "calendar-alert"
EXPORT_ICON = "download"
EXCEL_ICON = "file-spreadsheet"
PDF_ICON = "file-text"
PRINT_ICON = "printer"
VIEW_ICON = "eye"
EDIT_ICON = "pencil"
DELETE_ICON = "trash"
ATTACHMENT_ICON = "paperclip"
SAVE_ICON = "save"
SEARCH_ICON = "search"
FILTER_ICON = "filter"
RESET_ICON = "rotate-ccw"
BACKUP_ICON = "database-backup"
LANGUAGE_ICON = "languages"
SUN_ICON = "sun"
MOON_ICON = "moon"
BELL_ICON = "bell"
USER_ICON = "user"
CHEVRON_LEFT_ICON = "chevron-left"
CHEVRON_RIGHT_ICON = "chevron-right"
FOLDER_OPEN_ICON = "folder-open"

ICON_ALIASES = {
    "supplier-add": "building-plus",
    "pay": PAID_ICON,
    "unpaid": UNPAID_ICON,
    "complete": PAID_ICON,
    "warning": WARNING_ICON,
    "urgent": "flame",
    "normal": PAID_ICON,
    "critical": CRITICAL_ICON,
    "choose": FOLDER_OPEN_ICON,
    "pdf": PDF_ICON,
    "excel": EXCEL_ICON,
}


@lru_cache(maxsize=256)
def _read_svg(name: str) -> str:
    resolved = ICON_ALIASES.get(name, name)
    path = ICON_DIR / f"{resolved}.svg"
    if not path.exists():
        path = ICON_DIR / "circle-help.svg"
    return path.read_text(encoding="utf-8")


def icon_pixmap(name: str, color: str = COLOR_MUTED_DARK, size: int = 18) -> QPixmap:
    svg = _read_svg(name).replace("currentColor", color)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter)
    painter.end()
    return pixmap


def app_icon(name: str, color: str = COLOR_MUTED_DARK, size: int = 18) -> QIcon:
    return QIcon(icon_pixmap(name, color, size))


def recolor_icon(icon_name: str, active: bool = False, danger: bool = False, theme: str = "dark", size: int = 18) -> QIcon:
    if active:
        color = COLOR_WHITE if theme == "dark" else COLOR_PRIMARY
    elif danger:
        color = COLOR_WHITE
    else:
        color = COLOR_MUTED_DARK if theme == "dark" else COLOR_MUTED_LIGHT
    return app_icon(icon_name, color, size)


def icon_size(size: int) -> QSize:
    return QSize(size, size)


def readable_on(accent: str) -> str:
    color = QColor(accent)
    brightness = (color.red() * 299 + color.green() * 587 + color.blue() * 114) / 1000
    return "#0F172A" if brightness > 170 else COLOR_WHITE
