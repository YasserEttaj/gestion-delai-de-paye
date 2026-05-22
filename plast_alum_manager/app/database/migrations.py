from __future__ import annotations

from app.database.db import Base, engine


def initialize_database() -> None:
    from app.models import invoice_model, log_model, payment_model, setting_model, supplier_model, user_model  # noqa: F401

    Base.metadata.create_all(bind=engine)
