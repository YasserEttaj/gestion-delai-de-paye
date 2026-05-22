from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.db import Base


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    reference = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(String, default=now_iso, nullable=False)

    invoice = relationship("Invoice", back_populates="payments")
