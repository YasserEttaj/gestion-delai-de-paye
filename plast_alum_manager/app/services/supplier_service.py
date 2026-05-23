from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from app.database.db import session_scope
from app.models.invoice_model import Invoice
from app.models.supplier_model import Supplier
from app.services.log_service import LogService
from config import STATUS_PAID


class SupplierService:
    @staticmethod
    def _outstanding_amount(supplier: Supplier) -> float:
        total = 0.0
        for invoice in supplier.invoices:
            if invoice.status == STATUS_PAID:
                continue
            paid = sum(float(payment.amount or 0) for payment in invoice.payments)
            total += max(float(invoice.amount_ttc or 0) - paid, 0.0)
        return total

    @staticmethod
    def _clean(data: dict) -> dict:
        cleaned = {
            "name": (data.get("name") or "").strip(),
            "ice": (data.get("ice") or "").strip() or None,
            "if_number": (data.get("if_number") or "").strip() or None,
            "rc": (data.get("rc") or "").strip() or None,
            "address": (data.get("address") or "").strip() or None,
            "city": (data.get("city") or "").strip() or None,
            "phone": (data.get("phone") or "").strip() or None,
            "email": (data.get("email") or "").strip().lower() or None,
            "contact_person": (data.get("contact_person") or "").strip() or None,
            "rib": (data.get("rib") or "").strip() or None,
            "notes": (data.get("notes") or "").strip() or None,
        }
        if not cleaned["name"]:
            raise ValueError("Le nom fournisseur est obligatoire.")
        if cleaned["email"] and "@" not in cleaned["email"]:
            raise ValueError("Email fournisseur invalide.")
        return cleaned

    @staticmethod
    def _check_duplicate(session, data: dict, current_id: int | None = None) -> None:
        name_query = session.query(Supplier).filter(Supplier.name.ilike(data["name"]))
        if current_id:
            name_query = name_query.filter(Supplier.id != current_id)
        if name_query.first():
            raise ValueError("Un fournisseur avec ce nom existe déjà.")
        if data.get("ice"):
            ice_query = session.query(Supplier).filter(Supplier.ice == data["ice"])
            if current_id:
                ice_query = ice_query.filter(Supplier.id != current_id)
            if ice_query.first():
                raise ValueError("Un fournisseur avec cet ICE existe déjà.")

    @staticmethod
    def list_suppliers(search: str = "", city: str = "", sort_by: str = "name") -> list[dict]:
        with session_scope() as session:
            query = session.query(Supplier).options(selectinload(Supplier.invoices).selectinload(Invoice.payments))
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
            suppliers = query.all()
            return [
                {
                    "supplier": supplier,
                    "invoice_count": len(supplier.invoices),
                    "unpaid_amount": SupplierService._outstanding_amount(supplier),
                }
                for supplier in suppliers
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
        cleaned = SupplierService._clean(data)
        with session_scope() as session:
            SupplierService._check_duplicate(session, cleaned)
            supplier = Supplier(**cleaned)
            session.add(supplier)
            session.flush()
            LogService.log(session, user_id, "Add supplier", "supplier", supplier.id, supplier.name)
            return supplier

    @staticmethod
    def update_supplier(supplier_id: int, data: dict, user_id: int | None) -> None:
        cleaned = SupplierService._clean(data)
        with session_scope() as session:
            supplier = session.get(Supplier, supplier_id)
            if not supplier:
                raise ValueError("Fournisseur introuvable.")
            SupplierService._check_duplicate(session, cleaned, supplier_id)
            for key, value in cleaned.items():
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
