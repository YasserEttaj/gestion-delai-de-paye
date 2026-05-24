from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, Text, UniqueConstraint

from app.database.db import Base


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class NotificationState(Base):
    __tablename__ = "notification_states"
    __table_args__ = (
        UniqueConstraint("user_id", "alert_key", name="uq_notification_state_user_key"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_key = Column(String, nullable=False, index=True)
    level = Column(String, nullable=False, default="info")
    title = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    source = Column(String, nullable=True)
    read_at = Column(String, nullable=True)
    dismissed_at = Column(String, nullable=True)
    snoozed_until = Column(String, nullable=True)
    last_delivered_at = Column(String, nullable=True)
    delivery_count = Column(Integer, nullable=False, default=0)
    created_at = Column(String, default=now_iso, nullable=False)
    updated_at = Column(String, default=now_iso, onupdate=now_iso, nullable=False)
