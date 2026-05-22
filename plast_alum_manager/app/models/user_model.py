from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(String, default=now_iso, nullable=False)
    updated_at = Column(String, default=now_iso, onupdate=now_iso, nullable=False)
    last_login = Column(String, nullable=True)

    invoices = relationship("Invoice", back_populates="creator")
    logs = relationship("ActivityLog", back_populates="user")
