from __future__ import annotations

import sys
from pathlib import Path


SOURCE_DIR = Path(__file__).resolve().parent

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
    RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", BASE_DIR))
else:
    BASE_DIR = SOURCE_DIR
    RESOURCE_DIR = SOURCE_DIR

DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"
EXPORT_DIR = DATA_DIR / "exports"
UPLOAD_DIR = DATA_DIR / "uploads"
DATABASE_PATH = DATA_DIR / "database.sqlite"
TRANSLATION_DIR = RESOURCE_DIR / "app" / "translations"
ASSETS_DIR = RESOURCE_DIR / "app" / "assets"
USER_ASSETS_DIR = DATA_DIR / "assets"
USER_LOGO_PATH = USER_ASSETS_DIR / "logo.png"
BUNDLED_LOGO_PATH = ASSETS_DIR / "logo.png"
LOGO_PATH = USER_LOGO_PATH if USER_LOGO_PATH.exists() else BUNDLED_LOGO_PATH
APP_ICON_PATH = ASSETS_DIR / "icons" / "app.ico"


APP_NAME = "PLAST ALUM - Gestion des Paiements Fournisseurs"
COMPANY_NAME = "PLAST ALUM"
MIN_WIDTH = 1200
MIN_HEIGHT = 750


DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_EMAIL = "admin@plast-alum.local"


DEFAULT_SETTINGS = {
    "company_name": COMPANY_NAME,
    "app_title": APP_NAME,
    "default_language": "fr",
    "default_theme": "dark",
    "currency": "MAD",
    "date_format": "%d/%m/%Y",
    "normal_max_days": "40",
    "attention_min_days": "41",
    "attention_max_days": "49",
    "urgent_min_days": "50",
    "urgent_max_days": "59",
    "critical_min_days": "60",
    "backup_folder": str(BACKUP_DIR),
    "auto_backup_on_close": "true",
    "auto_backup_keep": "10",
    "high_unpaid_amount": "50000",
}


ROLE_ADMIN = "Admin"
ROLE_ACCOUNTANT = "Comptable"
ROLE_VIEWER = "Viewer"

STATUS_PAID = "paid"
STATUS_UNPAID = "unpaid"
STATUS_PARTIAL = "partial"

STATUS_LABELS_FR = {
    STATUS_PAID: "Payée",
    STATUS_UNPAID: "Non payée",
    STATUS_PARTIAL: "Partiellement payée",
}

STATUS_LABELS_AR = {
    STATUS_PAID: "مدفوعة",
    STATUS_UNPAID: "غير مدفوعة",
    STATUS_PARTIAL: "مدفوعة جزئيا",
}

PAYMENT_METHODS = [
    "Virement bancaire",
    "Chèque",
    "Espèces",
    "Carte",
    "Autre",
]


def ensure_directories() -> None:
    for directory in (DATA_DIR, BACKUP_DIR, EXPORT_DIR, UPLOAD_DIR, USER_ASSETS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
