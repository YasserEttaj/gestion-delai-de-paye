from __future__ import annotations

from sqlalchemy import case, func, or_

from app.database.db import session_scope
from app.models.invoice_model import Invoice
from app.models.supplier_model import Supplier
from app.services.log_service import LogService
from config import STATUS_PAID


class SupplierService:
    @staticmethod
    def list_suppliers(search: str = "", city: str = "", sort_by: str = "name") -> list[dict]:
        with session_scope() as session:
            unpaid_sum = func.coalesce(func.sum(case((Invoice.status != STATUS_PAID, Invoice.amount_ttc), else_=0)), 0)
            query = (
                session.query(
                    Supplier,
                    func.count(Invoice.id).label("invoice_count"),
                    unpaid_sum.label("unpaid_amount"),
                )
                .outerjoin(Invoice)
                .group_by(Supplier.id)
            )
            if search:
                like = f"%{search}%"
                query = query.filter(
                    or_(
                        Supplier.name.ilike(like),
                        Supplier.ice.ilike(like),
                        Supplier.phone.ilike(like),
                        Supplier.city.ilike(like),
                    )
                )
            if city:
                query = query.filter(Supplier.city == city)
            if sort_by == "city":
                query = query.order_by(Supplier.city.asc(), Supplier.name.asc())
            elif sort_by == "date":
                query = query.order_by(Supplier.created_at.desc())
            else:
                query = query.order_by(Supplier.name.asc())
            return [
                {"supplier": supplier, "invoice_count": int(invoice_count or 0), "unpaid_amount": float(unpaid_amount or 0)}
                for supplier, invoice_count, unpaid_amount in query.all()
            ]

    @staticmethod
    def get_cities() -> list[str]:
        with session_scope() as session:
            rows = session.query(Supplier.city).filter(Supplier.city.is_not(None), Supplier.city != "").distinct().order_by(Supplier.city).all()
            return [row[0] for row in rows]

    @staticmethod
    def get_all() -> list[Supplier]:
        with session_scope() as session:
            return list(session.query(Supplier).order_by(Supplier.name.asc()).all())

    @staticmethod
    def get_supplier(supplier_id: int) -> Supplier | None:
        with session_scope() as session:
            return session.get(Supplier, supplier_id)

    @staticmethod
    def create_supplier(data: dict, user_id: int | None) -> Supplier:
        with session_scope() as session:
            supplier = Supplier(**data)
            session.add(supplier)
            session.flush()
            LogService.log(session, user_id, "Add supplier", "supplier", supplier.id, supplier.name)
            return supplier

    @staticmethod
    def update_supplier(supplier_id: int, data: dict, user_id: int | None) -> None:
        with session_scope() as session:
            supplier = session.get(Supplier, supplier_id)
            if not supplier:
                raise ValueError("Fournisseur introuvable.")
            for key, value in data.items():
                setattr(supplier, key, value)
            LogService.log(session, user_id, "Edit supplier", "supplier", supplier.id, supplier.name)

    @staticmethod
    def delete_supplier(supplier_id: int, user_id: int | None) -> None:
        with session_scope() as session:
            supplier = session.get(Supplier, supplier_id)
            if not supplier:
                raise ValueError("Fournisseur introuvable.")
            LogService.log(session, user_id, "Delete supplier", "supplier", supplier.id, supplier.name)
            session.delete(supplier)
