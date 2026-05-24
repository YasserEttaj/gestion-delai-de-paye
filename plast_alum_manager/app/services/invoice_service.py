from __future__ import annotations

import shutil
from datetime import date, timedelta
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


VALID_INVOICE_STATUSES = {STATUS_PAID, STATUS_PARTIAL, STATUS_UNPAID}


class InvoiceService:
    @staticmethod
    def _parse_money(value, field: str, *, allow_zero: bool = True) -> float:
        if value in (None, ""):
            return 0.0
        try:
            amount = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field} doit être un nombre valide.")
        if amount < 0 or (not allow_zero and amount <= 0):
            raise ValueError(f"{field} doit être positif.")
        return amount

    @staticmethod
    def _paid_amount(invoice: Invoice) -> float:
        amount = float(invoice.amount_ttc or 0)
        payments_total = float(sum(payment.amount or 0 for payment in invoice.payments))
        if invoice.status == STATUS_PAID and payments_total <= 0:
            return amount
        return min(payments_total, amount)

    @staticmethod
    def _parse_iso_date(value: str | None, field: str, required: bool = True) -> str | None:
        if value in (None, ""):
            if required:
                raise ValueError(f"{field} est obligatoire.")
            return None
        parsed = DeadlineService.parse_date(str(value))
        if not parsed:
            raise ValueError(f"{field} est invalide.")
        return parsed.isoformat()

    @staticmethod
    def _clean_invoice_data(session, data: dict, current_invoice: Invoice | None = None) -> dict:
        cleaned = dict(data)
        if "amount_tva" not in cleaned and "tva_amount" in cleaned:
            cleaned["amount_tva"] = cleaned.get("tva_amount")
        try:
            supplier_id = int(cleaned.get("supplier_id"))
        except (TypeError, ValueError):
            raise ValueError("Le fournisseur est obligatoire.")
        if not session.get(Supplier, supplier_id):
            raise ValueError("Fournisseur introuvable.")

        invoice_number = (cleaned.get("invoice_number") or "").strip()
        if not invoice_number:
            raise ValueError("Le numéro de facture est obligatoire.")
        status = cleaned.get("status") or STATUS_UNPAID
        if status not in VALID_INVOICE_STATUSES:
            raise ValueError("Statut de facture invalide.")

        amount_ht = InvoiceService._parse_money(cleaned.get("amount_ht"), "Montant HT")
        tva_rate = InvoiceService._parse_money(cleaned.get("tva_rate"), "Taux TVA")
        amount_tva = InvoiceService._parse_money(cleaned.get("amount_tva"), "Montant TVA")
        amount_ttc = InvoiceService._parse_money(cleaned.get("amount_ttc"), "Montant TTC", allow_zero=False)
        if amount_ttc <= 0:
            raise ValueError("Le montant TTC doit être positif.")

        payment_date = InvoiceService._parse_iso_date(cleaned.get("payment_date"), "Date paiement", required=False)
        payment_method = (cleaned.get("payment_method") or "").strip() or None
        if status == STATUS_PAID and not payment_date:
            raise ValueError("La date paiement est obligatoire pour une facture payée.")
        if status == STATUS_PAID and not payment_method:
            raise ValueError("Le mode paiement est obligatoire pour une facture payée.")

        if current_invoice is not None:
            paid = sum(float(payment.amount or 0) for payment in current_invoice.payments)
            if paid > amount_ttc:
                raise ValueError("Le montant TTC ne peut pas être inférieur aux paiements déjà enregistrés.")

        return {
            "supplier_id": supplier_id,
            "invoice_number": invoice_number,
            "invoice_date": InvoiceService._parse_iso_date(cleaned.get("invoice_date"), "Date facture"),
            "reception_date": InvoiceService._parse_iso_date(cleaned.get("reception_date"), "Date réception", required=False),
            "due_date": InvoiceService._parse_iso_date(cleaned.get("due_date"), "Date échéance", required=False),
            "amount_ht": amount_ht,
            "tva_rate": tva_rate,
            "amount_tva": amount_tva,
            "amount_ttc": amount_ttc,
            "status": status,
            "payment_date": payment_date if status == STATUS_PAID else None,
            "payment_method": payment_method if status == STATUS_PAID else None,
            "notes": (cleaned.get("notes") or "").strip() or None,
        }

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
                parsed = DeadlineService.parse_date(str(filters["date_from"]))
                if parsed:
                    query = query.filter(Invoice.invoice_date >= parsed.isoformat())
            if filters.get("date_to"):
                parsed = DeadlineService.parse_date(str(filters["date_to"]))
                if parsed:
                    query = query.filter(Invoice.invoice_date <= parsed.isoformat())
            if filters.get("amount_min") not in (None, ""):
                try:
                    query = query.filter(Invoice.amount_ttc >= float(filters["amount_min"]))
                except (TypeError, ValueError):
                    pass
            if filters.get("amount_max") not in (None, ""):
                try:
                    query = query.filter(Invoice.amount_ttc <= float(filters["amount_max"]))
                except (TypeError, ValueError):
                    pass

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
        attachment = data.get("attachment_source")
        with session_scope() as session:
            data = cls._clean_invoice_data(session, data)
            cls._check_duplicate(session, int(data["supplier_id"]), data["invoice_number"])
            if attachment:
                data["attachment_path"] = cls.copy_attachment(attachment)
            invoice = Invoice(**data, created_by=user_id)
            session.add(invoice)
            session.flush()
            LogService.log(session, user_id, "Add invoice", "invoice", invoice.id, invoice.invoice_number)
            return invoice

    @classmethod
    def update_invoice(cls, invoice_id: int, data: dict, user_id: int | None) -> None:
        attachment = data.get("attachment_source")
        with session_scope() as session:
            invoice = (
                session.query(Invoice)
                .options(selectinload(Invoice.payments))
                .filter(Invoice.id == invoice_id)
                .first()
            )
            if not invoice:
                raise ValueError("Facture introuvable.")
            merged = {
                "supplier_id": invoice.supplier_id,
                "invoice_number": invoice.invoice_number,
                "invoice_date": invoice.invoice_date,
                "reception_date": invoice.reception_date,
                "due_date": invoice.due_date,
                "amount_ht": invoice.amount_ht,
                "tva_rate": invoice.tva_rate,
                "amount_tva": invoice.amount_tva,
                "amount_ttc": invoice.amount_ttc,
                "status": invoice.status,
                "payment_date": invoice.payment_date,
                "payment_method": invoice.payment_method,
                "notes": invoice.notes,
            }
            merged.update(data)
            data = cls._clean_invoice_data(session, merged, invoice)
            cls._check_duplicate(session, int(data["supplier_id"]), data["invoice_number"], invoice_id)
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
    def mark_unpaid(invoice_id: int, user_id: int | None) -> None:
        with session_scope() as session:
            invoice = (
                session.query(Invoice)
                .options(selectinload(Invoice.payments))
                .filter(Invoice.id == invoice_id)
                .first()
            )
            if not invoice:
                raise ValueError("Facture introuvable.")
            if invoice.status == STATUS_UNPAID and not invoice.payments:
                raise ValueError("Cette facture est déjà non payée.")
            for payment in list(invoice.payments):
                session.delete(payment)
            invoice.status = STATUS_UNPAID
            invoice.payment_date = None
            invoice.payment_method = None
            LogService.log(session, user_id, "Mark invoice as unpaid", "invoice", invoice.id, invoice.invoice_number)

    @staticmethod
    def mark_paid(invoice_id: int, payment_date: str, payment_method: str, user_id: int | None) -> None:
        with session_scope() as session:
            invoice = (
                session.query(Invoice)
                .options(selectinload(Invoice.payments))
                .filter(Invoice.id == invoice_id)
                .first()
            )
            if not invoice:
                raise ValueError("Facture introuvable.")
            if invoice.status == STATUS_PAID:
                raise ValueError("Cette facture est déjà payée.")
            payment_date = InvoiceService._parse_iso_date(payment_date, "Date paiement")
            payment_method = (payment_method or "").strip()
            if not payment_method:
                raise ValueError("Le mode paiement est obligatoire.")
            outstanding = max(float(invoice.amount_ttc or 0) - sum(float(payment.amount or 0) for payment in invoice.payments), 0.0)
            if outstanding <= 0:
                raise ValueError("Aucun montant restant à payer.")
            invoice.status = STATUS_PAID
            invoice.payment_date = payment_date
            invoice.payment_method = payment_method
            session.add(
                Payment(
                    invoice_id=invoice.id,
                    amount=outstanding,
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
            if invoice.status == STATUS_PAID:
                raise ValueError("Cette facture est déjà payée.")
            amount = InvoiceService._parse_money(amount, "Montant paiement", allow_zero=False)
            already_paid = sum(payment.amount or 0 for payment in invoice.payments)
            invoice_total = float(invoice.amount_ttc or 0)
            outstanding = max(invoice_total - already_paid, 0)
            if outstanding <= 0:
                raise ValueError("Aucun montant restant à payer.")
            if amount > outstanding:
                raise ValueError(f"Le paiement dépasse le reste à payer ({outstanding:.2f}).")
            payment_date = InvoiceService._parse_iso_date(payment_date, "Date paiement")
            payment_method = (payment_method or "").strip()
            if not payment_method:
                raise ValueError("Le mode paiement est obligatoire.")
            if already_paid + amount >= invoice_total:
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
                        "key": f"invoice_deadline:{invoice.id}",
                        "source": "invoice",
                        "kind": "invoice_deadline",
                        "level": row["deadline"].category,
                        "title": f"Facture {invoice.invoice_number} à surveiller",
                        "message": f"{invoice.supplier.name} - {row['deadline'].days} jours - {row['outstanding_amount']:.2f} MAD",
                        "invoice_id": invoice.id,
                        "supplier_id": invoice.supplier_id,
                    }
                )
                supplier_overdue[invoice.supplier_id] = supplier_overdue.get(invoice.supplier_id, 0) + 1
            if not invoice.attachment_path:
                notes.append(
                    {
                        "key": f"invoice_attachment:{invoice.id}",
                        "source": "invoice",
                        "kind": "missing_attachment",
                        "level": "attention",
                        "title": f"Pièce jointe manquante",
                        "message": f"Facture {invoice.invoice_number}",
                        "invoice_id": invoice.id,
                        "supplier_id": invoice.supplier_id,
                    }
                )
            if row["outstanding_amount"] >= high_amount:
                notes.append(
                    {
                        "key": f"invoice_high_amount:{invoice.id}",
                        "source": "invoice",
                        "kind": "high_amount",
                        "level": "critical",
                        "title": "Montant impayé élevé",
                        "message": f"{invoice.invoice_number} - {row['outstanding_amount']:.2f} MAD",
                        "invoice_id": invoice.id,
                        "supplier_id": invoice.supplier_id,
                    }
                )
        suppliers = {supplier.id: supplier.name for supplier in [row["supplier"] for row in rows]}
        for supplier_id, count in supplier_overdue.items():
            if count >= 2:
                notes.append(
                    {
                        "key": f"supplier_overdue:{supplier_id}",
                        "source": "supplier",
                        "kind": "supplier_summary",
                        "level": "critical",
                        "title": "Fournisseur avec plusieurs retards",
                        "message": f"{suppliers.get(supplier_id, 'Fournisseur')} - {count} factures",
                        "invoice_id": None,
                        "supplier_id": supplier_id,
                    }
                )
        return notes[:50]

    @staticmethod
    def today_iso() -> str:
        return date.today().isoformat()

    @staticmethod
    def default_due_date(invoice_date: str | None, reception_date: str | None = None, days: int = 60) -> str | None:
        start = DeadlineService.parse_date(reception_date) or DeadlineService.parse_date(invoice_date)
        if not start:
            return None
        return (start + timedelta(days=days)).isoformat()
