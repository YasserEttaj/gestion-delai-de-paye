from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.db import Base
from config import STATUS_UNPAID


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("supplier_id", "invoice_number", name="uq_supplier_invoice_number"),
    )

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_number = Column(String, nullable=False, index=True)
    invoice_date = Column(String, nullable=False)
    reception_date = Column(String, nullable=True)
    due_date = Column(String, nullable=True)
    amount_ht = Column(Float, default=0.0, nullable=False)
    tva_rate = Column(Float, default=20.0, nullable=False)
    amount_tva = Column(Float, default=0.0, nullable=False)
    amount_ttc = Column(Float, default=0.0, nullable=False)
    status = Column(String, default=STATUS_UNPAID, nullable=False, index=True)
    payment_date = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    attachment_path = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(String, default=now_iso, nullable=False)
    updated_at = Column(String, default=now_iso, onupdate=now_iso, nullable=False)

    supplier = relationship("Supplier", back_populates="invoices")
    creator = relationship("User", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
