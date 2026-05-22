from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from app.database.db import session_scope
from app.services.log_service import LogService
from app.services.settings_service import SettingsService
from config import BACKUP_DIR, DATABASE_PATH


class BackupService:
    @staticmethod
    def backup_dir() -> Path:
        configured = SettingsService.get("backup_folder", str(BACKUP_DIR))
        return Path(configured or BACKUP_DIR)

    @staticmethod
    def create_backup(user_id: int | None = None, keep_last: int = 10) -> Path:
        if not DATABASE_PATH.exists():
            raise FileNotFoundError("Base de données introuvable.")
        backup_dir = BackupService.backup_dir()
        backup_dir.mkdir(parents=True, exist_ok=True)
        path = backup_dir / f"database_backup_{datetime.now():%Y%m%d_%H%M%S}.sqlite"
        shutil.copy2(DATABASE_PATH, path)
        backups = sorted(backup_dir.glob("database_backup_*.sqlite"), key=lambda item: item.stat().st_mtime, reverse=True)
        for old in backups[keep_last:]:
            old.unlink(missing_ok=True)
        with session_scope() as session:
            LogService.log(session, user_id, "Create backup", "database", None, str(path))
        return path

    @staticmethod
    def restore_backup(backup_file: str, user_id: int | None = None) -> None:
        source = Path(backup_file)
        if not source.exists():
            raise FileNotFoundError("Fichier de sauvegarde introuvable.")
        if source.suffix.lower() != ".sqlite":
            raise ValueError("Veuillez choisir un fichier SQLite valide.")
        shutil.copy2(source, DATABASE_PATH)
        with session_scope() as session:
            LogService.log(session, user_id, "Restore backup", "database", None, str(source))
