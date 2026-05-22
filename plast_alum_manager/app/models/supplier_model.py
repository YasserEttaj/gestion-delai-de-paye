from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.db import Base


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    ice = Column(String, nullable=True, index=True)
    if_number = Column(String, nullable=True)
    rc = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    contact_person = Column(String, nullable=True)
    rib = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(String, default=now_iso, nullable=False)
    updated_at = Column(String, default=now_iso, onupdate=now_iso, nullable=False)

    invoices = relationship("Invoice", back_populates="supplier", cascade="all, delete-orphan")
