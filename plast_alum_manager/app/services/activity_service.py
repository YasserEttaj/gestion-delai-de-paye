from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.database.db import session_scope
from app.models.log_model import ActivityLog
from app.models.user_model import User


class ActivityService:
    @staticmethod
    def list_logs(filters: dict | None = None, limit: int = 500) -> list[ActivityLog]:
        filters = filters or {}
        with session_scope() as session:
            query = session.query(ActivityLog).options(joinedload(ActivityLog.user)).outerjoin(User)
            if filters.get("search"):
                like = f"%{filters['search']}%"
                query = query.filter(or_(ActivityLog.action.ilike(like), ActivityLog.details.ilike(like), User.username.ilike(like)))
            if filters.get("action"):
                query = query.filter(ActivityLog.action.ilike(f"%{filters['action']}%"))
            if filters.get("user_id"):
                query = query.filter(ActivityLog.user_id == int(filters["user_id"]))
            if filters.get("date_from"):
                query = query.filter(ActivityLog.created_at >= filters["date_from"])
            if filters.get("date_to"):
                query = query.filter(ActivityLog.created_at <= filters["date_to"])
            return list(query.order_by(ActivityLog.created_at.desc()).limit(limit).all())
