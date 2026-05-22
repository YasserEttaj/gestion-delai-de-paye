from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from uuid import uuid4

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload, selectinload

from app.database.db import session_scope
from app.models.invoice_model import Invoice
from app.models.payment_model import Payment
from app.models.supplier_model import Supplier
from app.services.deadline_service import DeadlineService
from app.services.log_service import LogService
from app.services.settings_service import SettingsService
from config import STATUS_PAID, STATUS_PARTIAL, STATUS_UNPAID, UPLOAD_DIR


class InvoiceService:
    @staticmethod
    def _paid_amount(invoice: Invoice) -> float:
        if invoice.status == STATUS_PAID:
            return float(invoice.amount_ttc or 0)
        return float(sum(payment.amount or 0 for payment in invoice.payments))

    @classmethod
    def _row(cls, invoice: Invoice, settings: dict[str, str] | None = None) -> dict:
        paid = cls._paid_amount(invoice)
        amount = float(invoice.amount_ttc or 0)
        return {
            "invoice": invoice,
            "supplier": invoice.supplier,
            "deadline": DeadlineService.calculate(invoice, settings),
            "paid_amount": paid,
            "outstanding_amount": max(amount - paid, 0),
        }

    @staticmethod
    def copy_attachment(path: str | None) -> str | None:
        if not path:
            return None
        source = Path(path)
        if not source.exists():
            raise FileNotFoundError("Pièce jointe introuvable.")
        if source.suffix.lower() not in {".pdf", ".jpg", ".jpeg", ".png"}:
            raise ValueError("Formats autorisés : PDF, JPG, PNG.")
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        target = UPLOAD_DIR / f"{uuid4().hex}{source.suffix.lower()}"
        shutil.copy2(source, target)
        return str(target)

    @classmethod
    def list_invoices(cls, filters: dict | None = None) -> list[dict]:
        filters = filters or {}
        settings = SettingsService.all()
        with session_scope() as session:
            query = (
                session.query(Invoice)
                .options(joinedload(Invoice.supplier), selectinload(Invoice.payments))
                .join(Supplier)
            )
            search = filters.get("search", "").strip()
            if search:
                like = f"%{search}%"
                query = query.filter(or_(Invoice.invoice_number.ilike(like), Supplier.name.ilike(like)))
            if filters.get("status"):
                query = query.filter(Invoice.status == filters["status"])
            if filters.get("supplier_id"):
                query = query.filter(Invoice.supplier_id == int(filters["supplier_id"]))
            if filters.get("date_from"):
                query = query.filter(Invoice.invoice_date >= filters["date_from"])
            if filters.get("date_to"):
                query = query.filter(Invoice.invoice_date <= filters["date_to"])
            if filters.get("amount_min") not in (None, ""):
                query = query.filter(Invoice.amount_ttc >= float(filters["amount_min"]))
            if filters.get("amount_max") not in (None, ""):
                query = query.filter(Invoice.amount_ttc <= float(filters["amount_max"]))

            sort_by = filters.get("sort_by", "date_desc")
            if sort_by == "amount":
                query = query.order_by(Invoice.amount_ttc.desc())
            elif sort_by == "date_asc":
                query = query.order_by(Invoice.invoice_date.asc())
            else:
                query = query.order_by(Invoice.invoice_date.desc(), Invoice.id.desc())

            rows = [cls._row(invoice, settings) for invoice in query.all()]
            if filters.get("deadline_category"):
                rows = [row for row in rows if row["deadline"].category == filters["deadline_category"]]
            if sort_by == "days":
                rows.sort(key=lambda row: row["deadline"].days, reverse=True)
            return rows

    @staticmethod
    def get_invoice(invoice_id: int) -> Invoice | None:
        with session_scope() as session:
            return (
                session.query(Invoice)
                .options(joinedload(Invoice.supplier), selectinload(Invoice.payments))
                .filter(Invoice.id == invoice_id)
                .first()
            )

    @staticmethod
    def _check_duplicate(session, supplier_id: int, invoice_number: str, current_id: int | None = None) -> None:
        query = session.query(Invoice).filter(
            Invoice.supplier_id == supplier_id,
            Invoice.invoice_number == invoice_number.strip(),
        )
        if current_id:
            query = query.filter(Invoice.id != current_id)
        if query.first():
            raise ValueError("Ce numéro de facture existe déjà pour ce fournisseur.")

    @classmethod
    def create_invoice(cls, data: dict, user_id: int | None) -> Invoice:
        with session_scope() as session:
            cls._check_duplicate(session, int(data["supplier_id"]), data["invoice_number"])
            attachment = data.pop("attachment_source", None)
            if attachment:
                data["attachment_path"] = cls.copy_attachment(attachment)
            invoice = Invoice(**data, created_by=user_id)
            session.add(invoice)
            session.flush()
            LogService.log(session, user_id, "Add invoice", "invoice", invoice.id, invoice.invoice_number)
            return invoice

    @classmethod
    def update_invoice(cls, invoice_id: int, data: dict, user_id: int | None) -> None:
        with session_scope() as session:
            invoice = session.get(Invoice, invoice_id)
            if not invoice:
                raise ValueError("Facture introuvable.")
            cls._check_duplicate(session, int(data["supplier_id"]), data["invoice_number"], invoice_id)
            attachment = data.pop("attachment_source", None)
            if attachment:
                data["attachment_path"] = cls.copy_attachment(attachment)
            for key, value in data.items():
                setattr(invoice, key, value)
            LogService.log(session, user_id, "Edit invoice", "invoice", invoice.id, invoice.invoice_number)

    @staticmethod
    def delete_invoice(invoice_id: int, user_id: int | None) -> None:
        with session_scope() as session:
            invoice = session.get(Invoice, invoice_id)
            if not invoice:
                raise ValueError("Facture introuvable.")
            LogService.log(session, user_id, "Delete invoice", "invoice", invoice.id, invoice.invoice_number)
            session.delete(invoice)

    @staticmethod
    def mark_paid(invoice_id: int, payment_date: str, payment_method: str, user_id: int | None) -> None:
        with session_scope() as session:
            invoice = session.get(Invoice, invoice_id)
            if not invoice:
                raise ValueError("Facture introuvable.")
            invoice.status = STATUS_PAID
            invoice.payment_date = payment_date
            invoice.payment_method = payment_method
            session.add(
                Payment(
                    invoice_id=invoice.id,
                    amount=float(invoice.amount_ttc or 0),
                    payment_date=payment_date,
                    payment_method=payment_method,
                    reference="Paiement complet",
                )
            )
            LogService.log(session, user_id, "Mark invoice as paid", "invoice", invoice.id, invoice.invoice_number)

    @staticmethod
    def add_payment(invoice_id: int, amount: float, payment_date: str, payment_method: str, reference: str, notes: str, user_id: int | None) -> None:
        with session_scope() as session:
            invoice = (
                session.query(Invoice)
                .options(selectinload(Invoice.payments))
                .filter(Invoice.id == invoice_id)
                .first()
            )
            if not invoice:
                raise ValueError("Facture introuvable.")
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Le montant du paiement doit être positif.")
            already_paid = sum(payment.amount or 0 for payment in invoice.payments)
            if already_paid + amount >= float(invoice.amount_ttc or 0):
                invoice.status = STATUS_PAID
                invoice.payment_date = payment_date
                invoice.payment_method = payment_method
            else:
                invoice.status = STATUS_PARTIAL
            session.add(
                Payment(
                    invoice_id=invoice.id,
                    amount=amount,
                    payment_date=payment_date,
                    payment_method=payment_method,
                    reference=reference,
                    notes=notes,
                )
            )
            LogService.log(session, user_id, "Add payment", "invoice", invoice.id, f"{amount:.2f}")

    @classmethod
    def dashboard_stats(cls) -> dict:
        rows = cls.list_invoices({})
        with session_scope() as session:
            total_suppliers = session.query(func.count(Supplier.id)).scalar() or 0
        total_invoices = len(rows)
        paid = [row for row in rows if row["invoice"].status == STATUS_PAID]
        unpaid = [row for row in rows if row["invoice"].status == STATUS_UNPAID]
        partial = [row for row in rows if row["invoice"].status == STATUS_PARTIAL]
        late = [row for row in rows if row["invoice"].status != STATUS_PAID and row["deadline"].days > 40]
        critical = [row for row in rows if row["invoice"].status != STATUS_PAID and row["deadline"].category == "critical"]
        return {
            "total_suppliers": total_suppliers,
            "total_invoices": total_invoices,
            "paid_count": len(paid),
            "unpaid_count": len(unpaid),
            "partial_count": len(partial),
            "late_count": len(late),
            "unpaid_amount": sum(row["outstanding_amount"] for row in rows if row["invoice"].status != STATUS_PAID),
            "paid_amount": sum(row["paid_amount"] for row in rows),
            "critical_count": len(critical),
            "rows": rows,
            "critical_rows": critical[:10],
            "urgent_rows": [row for row in rows if row["deadline"].category == "urgent"][:10],
        }

    @classmethod
    def notifications(cls) -> list[dict]:
        settings = SettingsService.all()
        high_amount = float(settings.get("high_unpaid_amount", 50000) or 50000)
        rows = cls.list_invoices({})
        notes: list[dict] = []
        supplier_overdue: dict[int, int] = {}
        for row in rows:
            invoice = row["invoice"]
            if invoice.status == STATUS_PAID:
                continue
            if row["deadline"].days > 40:
                notes.append(
                    {
                        "level": row["deadline"].category,
                        "title": f"Facture {invoice.invoice_number} à surveiller",
                        "message": f"{invoice.supplier.name} - {row['deadline'].days} jours - {row['outstanding_amount']:.2f} MAD",
                        "invoice_id": invoice.id,
                    }
                )
                supplier_overdue[invoice.supplier_id] = supplier_overdue.get(invoice.supplier_id, 0) + 1
            if not invoice.attachment_path:
                notes.append(
                    {
                        "level": "attention",
                        "title": f"Pièce jointe manquante",
                        "message": f"Facture {invoice.invoice_number}",
                        "invoice_id": invoice.id,
                    }
                )
            if row["outstanding_amount"] >= high_amount:
                notes.append(
                    {
                        "level": "critical",
                        "title": "Montant impayé élevé",
                        "message": f"{invoice.invoice_number} - {row['outstanding_amount']:.2f} MAD",
                        "invoice_id": invoice.id,
                    }
                )
        suppliers = {supplier.id: supplier.name for supplier in [row["supplier"] for row in rows]}
        for supplier_id, count in supplier_overdue.items():
            if count >= 2:
                notes.append(
                    {
                        "level": "critical",
                        "title": "Fournisseur avec plusieurs retards",
                        "message": f"{suppliers.get(supplier_id, 'Fournisseur')} - {count} factures",
                        "invoice_id": None,
                    }
                )
        return notes[:50]

    @staticmethod
    def today_iso() -> str:
        return date.today().isoformat()
