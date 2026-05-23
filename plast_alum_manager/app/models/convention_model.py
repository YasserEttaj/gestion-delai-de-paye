from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text

from app.database.db import Base


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Convention(Base):
    __tablename__ = "conventions"

    id = Column(Integer, primary_key=True)
    company_name = Column(String, nullable=False, index=True)
    convention_number = Column(String, nullable=False, unique=True, index=True)
    convention_type = Column(String, nullable=False, index=True)
    start_date = Column(String, nullable=False)
    deadline_days = Column(Integer, nullable=False)
    due_date = Column(String, nullable=False, index=True)
    remaining_days = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, index=True, default="active")
    notes = Column(Text, nullable=True)
    created_at = Column(String, default=now_iso, nullable=False)
    updated_at = Column(String, default=now_iso, onupdate=now_iso, nullable=False)
