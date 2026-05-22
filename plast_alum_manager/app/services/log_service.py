from __future__ import annotations

from app.models.log_model import ActivityLog


class LogService:
    @staticmethod
    def log(session, user_id: int | None, action: str, entity_type: str | None = None, entity_id: int | None = None, details: str | None = None) -> None:
        session.add(
            ActivityLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details,
            )
        )
