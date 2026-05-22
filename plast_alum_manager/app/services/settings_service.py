from __future__ import annotations

from app.database.db import session_scope
from app.models.setting_model import Setting
from config import DEFAULT_SETTINGS


class SettingsService:
    @staticmethod
    def all() -> dict[str, str]:
        with session_scope() as session:
            existing = {row.key: row.value for row in session.query(Setting).all()}
            for key, value in DEFAULT_SETTINGS.items():
                existing.setdefault(key, str(value))
            return existing

    @staticmethod
    def get(key: str, default: str | None = None) -> str | None:
        with session_scope() as session:
            setting = session.query(Setting).filter_by(key=key).first()
            if setting:
                return setting.value
            return DEFAULT_SETTINGS.get(key, default)

    @staticmethod
    def set_many(values: dict[str, str], user_id: int | None = None) -> None:
        from app.services.log_service import LogService

        with session_scope() as session:
            for key, value in values.items():
                setting = session.query(Setting).filter_by(key=key).first()
                if setting:
                    setting.value = str(value)
                else:
                    session.add(Setting(key=key, value=str(value)))
            LogService.log(session, user_id, "Change settings", "settings", None, ", ".join(sorted(values.keys())))
