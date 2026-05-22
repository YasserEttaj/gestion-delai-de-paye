from __future__ import annotations

import argparse
import re
from datetime import date, datetime, time, timedelta
from pathlib import Path

from sqlalchemy import or_

from app.database.db import session_scope
from app.models.invoice_model import Invoice
from app.models.log_model import ActivityLog
from app.models.payment_model import Payment
from app.models.setting_model import Setting
from app.models.supplier_model import Supplier
from app.models.user_model import User
from app.services.auth_service import AuthService
from config import (
    DATABASE_PATH,
    DEFAULT_ADMIN_EMAIL,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    DEFAULT_SETTINGS,
    PAYMENT_METHODS,
    ROLE_ADMIN,
    STATUS_PAID,
    STATUS_PARTIAL,
    STATUS_UNPAID,
    UPLOAD_DIR,
)


DEMO_MARKER = "[DEMO_PLAST_ALUM]"
DEMO_ATTACHMENT_PREFIX = "demo_plast_alum_invoice_"


def seed_defaults() -> None:
    with session_scope() as session:
        for key, value in DEFAULT_SETTINGS.items():
            if not session.query(Setting).filter_by(key=key).first():
                session.add(Setting(key=key, value=str(value)))

        if not session.query(User).filter_by(username=DEFAULT_ADMIN_USERNAME).first():
            session.add(
                User(
                    username=DEFAULT_ADMIN_USERNAME,
                    full_name="Administrateur",
                    email=DEFAULT_ADMIN_EMAIL,
                    password_hash=AuthService.hash_password(DEFAULT_ADMIN_PASSWORD),
                    role=ROLE_ADMIN,
                    is_active=True,
                )
            )


DEMO_SUPPLIERS = [
    {
        "name": "Casa Profil Aluminium",
        "ice": "001527398000087",
        "if_number": "15273980",
        "rc": "CASA-219845",
        "address": "128 Zone Industrielle Sidi Bernoussi",
        "city": "Casablanca",
        "phone": "+212 522 34 18 90",
        "email": "facturation@casa-profil.ma",
        "contact_person": "Hassan El Amrani",
        "rib": "007780000123456789012345",
    },
    {
        "name": "Alumex Maroc SARL",
        "ice": "001849275000063",
        "if_number": "18492750",
        "rc": "CASA-308412",
        "address": "Lot 44 Parc Industriel Ouled Saleh",
        "city": "Casablanca",
        "phone": "+212 522 59 74 31",
        "email": "compta@alumexmaroc.ma",
        "contact_person": "Nadia Berrada",
        "rib": "021780000987654321098765",
    },
    {
        "name": "Marrakech Accessoires Alu",
        "ice": "002041638000051",
        "if_number": "20416380",
        "rc": "RAK-77412",
        "address": "15 Rue Ibn Tachfine, Quartier Industriel Sidi Ghanem",
        "city": "Marrakech",
        "phone": "+212 524 33 76 22",
        "email": "contact@marrakech-accessoires.ma",
        "contact_person": "Youssef Ait Lahcen",
        "rib": "011780000567890123456789",
    },
    {
        "name": "Atlas Anodisation Maroc",
        "ice": "001936574000029",
        "if_number": "19365740",
        "rc": "RAK-81605",
        "address": "Km 9 Route de Safi, Zone Industrielle",
        "city": "Marrakech",
        "phone": "+212 524 49 20 11",
        "email": "admin@atlas-anodisation.ma",
        "contact_person": "Samira El Fassi",
        "rib": "005780000246813579024681",
    },
    {
        "name": "Rabat Verre et Profiles",
        "ice": "001775436000094",
        "if_number": "17754360",
        "rc": "RAB-129845",
        "address": "22 Avenue Hassan II, Hay Nahda",
        "city": "Rabat",
        "phone": "+212 537 71 08 64",
        "email": "finance@rabatverre.ma",
        "contact_person": "Karim Bennani",
        "rib": "022780000333444555666777",
    },
    {
        "name": "Maghreb Joints et Accessoires",
        "ice": "002115908000038",
        "if_number": "21159080",
        "rc": "RAB-140286",
        "address": "63 Rue Al Massira, Temara",
        "city": "Rabat",
        "phone": "+212 537 61 55 28",
        "email": "reglement@maghreb-joints.ma",
        "contact_person": "Imane Tazi",
        "rib": "013780000112233445566778",
    },
    {
        "name": "Tanger Metal Facades",
        "ice": "001682049000074",
        "if_number": "16820490",
        "rc": "TNG-66318",
        "address": "Zone Franche TFZ, Lot 19",
        "city": "Tanger",
        "phone": "+212 539 39 84 70",
        "email": "compta@tangerfacades.ma",
        "contact_person": "Rachid El Ouardi",
        "rib": "019780000765432109876543",
    },
    {
        "name": "Nord Inox et Aluminium",
        "ice": "002287451000016",
        "if_number": "22874510",
        "rc": "TNG-70124",
        "address": "Route de Tetouan, Zone Industrielle Mghogha",
        "city": "Tanger",
        "phone": "+212 539 95 40 18",
        "email": "contact@nordinoxalu.ma",
        "contact_person": "Meryem Choukri",
        "rib": "007780000998877665544332",
    },
    {
        "name": "Fes Quincaillerie Aluminium",
        "ice": "001528604000052",
        "if_number": "15286040",
        "rc": "FES-55892",
        "address": "31 Avenue Allal El Fassi, Zone Bensouda",
        "city": "Fès",
        "phone": "+212 535 65 19 44",
        "email": "factures@fesquincaillerie.ma",
        "contact_person": "Omar Idrissi",
        "rib": "011780000135792468013579",
    },
    {
        "name": "Agadir Aluminium Services",
        "ice": "002009314000044",
        "if_number": "20093140",
        "rc": "AGA-44017",
        "address": "Bloc C, Zone Industrielle Ait Melloul",
        "city": "Agadir",
        "phone": "+212 528 24 63 59",
        "email": "support@agadir-alu.ma",
        "contact_person": "Amina Bouzid",
        "rib": "021780000102938475610293",
    },
]


def _demo_supplier_filter():
    return Supplier.notes.like(f"%{DEMO_MARKER}%")


def _demo_invoice_filter():
    return or_(Invoice.invoice_number.like("DEMO-%"), Invoice.notes.like(f"%{DEMO_MARKER}%"))


def _demo_log_filter():
    return ActivityLog.details.like(f"%{DEMO_MARKER}%")


def _demo_payment_filter(invoice_ids: list[int]):
    own_payment = or_(Payment.notes.like(f"%{DEMO_MARKER}%"), Payment.reference.like("DEMO-%"))
    if invoice_ids:
        return or_(Payment.invoice_id.in_(invoice_ids), own_payment)
    return own_payment


def _admin_user_id(session) -> int | None:
    admin = session.query(User).filter_by(username=DEFAULT_ADMIN_USERNAME).first()
    return admin.id if admin else None


def _money(amount: float) -> float:
    return round(float(amount), 2)


def _invoice_amounts(amount_ttc: float, tva_rate: float = 20.0) -> tuple[float, float, float]:
    amount_ht = _money(amount_ttc / (1 + tva_rate / 100))
    amount_tva = _money(amount_ttc - amount_ht)
    return amount_ht, amount_tva, _money(amount_ttc)


def _safe_filename(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_").lower()


def _write_demo_pdf(path: Path, invoice_number: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        pdf = canvas.Canvas(str(path), pagesize=A4)
        pdf.setTitle(f"Demo {invoice_number}")
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(72, 780, "PLAST ALUM - Piece jointe demo")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(72, 750, f"Facture: {invoice_number}")
        pdf.drawString(72, 730, "Document genere uniquement pour tester l'ouverture des pieces jointes.")
        pdf.drawString(72, 710, DEMO_MARKER)
        pdf.showPage()
        pdf.save()
    except Exception:
        path.write_bytes(
            b"%PDF-1.4\n"
            b"1 0 obj<<>>endobj\n"
            b"2 0 obj<< /Length 44 >>stream\nBT /F1 12 Tf 72 720 Td (PLAST ALUM demo invoice) Tj ET\nendstream endobj\n"
            b"3 0 obj<< /Type /Page /Parent 4 0 R /Contents 2 0 R >>endobj\n"
            b"4 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
            b"5 0 obj<< /Type /Catalog /Pages 4 0 R >>endobj\n"
            b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000030 00000 n \n0000000124 00000 n \n0000000191 00000 n \n0000000256 00000 n \n"
            b"trailer<< /Root 5 0 R /Size 6 >>\nstartxref\n321\n%%EOF\n"
        )


def _demo_attachment(invoice_number: str) -> str | None:
    filename = f"{DEMO_ATTACHMENT_PREFIX}{_safe_filename(invoice_number)}.pdf"
    target = UPLOAD_DIR / filename
    _write_demo_pdf(target, invoice_number)
    return str(target)


def demo_data_exists() -> bool:
    with session_scope() as session:
        return bool(
            session.query(Supplier.id).filter(_demo_supplier_filter()).first()
            or session.query(Invoice.id).filter(_demo_invoice_filter()).first()
        )


def remove_demo_data(remove_files: bool = True) -> dict[str, int]:
    """Remove only rows marked as PLAST ALUM demo data."""
    counts = {"suppliers": 0, "invoices": 0, "payments": 0, "activity_logs": 0, "attachments": 0}
    attachment_paths: list[str] = []
    with session_scope() as session:
        invoice_ids = [row[0] for row in session.query(Invoice.id).filter(_demo_invoice_filter()).all()]
        for payment in session.query(Payment).filter(_demo_payment_filter(invoice_ids)).all():
            session.delete(payment)
            counts["payments"] += 1
        for log in session.query(ActivityLog).filter(_demo_log_filter()).all():
            session.delete(log)
            counts["activity_logs"] += 1
        for invoice in session.query(Invoice).filter(_demo_invoice_filter()).all():
            if invoice.attachment_path:
                attachment_paths.append(invoice.attachment_path)
            session.delete(invoice)
            counts["invoices"] += 1
        for supplier in session.query(Supplier).filter(_demo_supplier_filter()).all():
            session.delete(supplier)
            counts["suppliers"] += 1

    if remove_files:
        upload_root = UPLOAD_DIR.resolve()
        for raw_path in attachment_paths:
            path = Path(raw_path)
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved.parent == upload_root and resolved.name.startswith(DEMO_ATTACHMENT_PREFIX) and resolved.exists():
                resolved.unlink()
                counts["attachments"] += 1
    return counts


def seed_demo_data(reset: bool = False) -> dict[str, int | bool]:
    """Insert realistic optional demo data. It is never called automatically."""
    if reset:
        remove_demo_data()
    elif demo_data_exists():
        return {"created": False, "suppliers": 0, "invoices": 0, "payments": 0, "activity_logs": 0}

    today = date.today()
    counts: dict[str, int | bool] = {"created": True, "suppliers": 0, "invoices": 0, "payments": 0, "activity_logs": 0}
    with session_scope() as session:
        admin_id = _admin_user_id(session)
        created_suppliers: list[Supplier] = []
        for data in DEMO_SUPPLIERS:
            supplier = Supplier(
                **data,
                notes=f"{DEMO_MARKER} Fournisseur de démonstration pour tests internes.",
            )
            session.add(supplier)
            created_suppliers.append(supplier)
            counts["suppliers"] = int(counts["suppliers"]) + 1
        session.flush()

        payment_methods = PAYMENT_METHODS or ["Virement bancaire", "Chèque", "Espèces", "Carte", "Autre"]
        for supplier_index, supplier in enumerate(created_suppliers, start=1):
            for sequence in range(1, 7):
                if sequence == 1:
                    status = STATUS_PAID
                    days_old = 16 + supplier_index % 8
                    amount_ttc = 7200 + supplier_index * 640
                elif sequence == 2:
                    status = STATUS_UNPAID
                    days_old = 27 + (supplier_index % 4) * 3
                    amount_ttc = 13200 + supplier_index * 1180
                elif sequence == 3:
                    status = STATUS_UNPAID
                    days_old = 42 + supplier_index % 8
                    amount_ttc = 24600 + supplier_index * 1470
                elif sequence == 4:
                    status = STATUS_UNPAID
                    days_old = 52 + supplier_index % 7 if supplier_index % 2 else 64 + (supplier_index % 5) * 4
                    amount_ttc = 49500 + supplier_index * 3250
                elif sequence == 5:
                    status = STATUS_PARTIAL
                    days_old = 47 + supplier_index % 5 if supplier_index % 2 else 66 + supplier_index % 9
                    amount_ttc = 38200 + supplier_index * 2780
                else:
                    status = STATUS_PAID
                    days_old = 69 + supplier_index % 12
                    amount_ttc = 18800 + supplier_index * 1730

                reception_date = today - timedelta(days=days_old)
                invoice_date = reception_date - timedelta(days=1 + supplier_index % 3)
                due_date = reception_date + timedelta(days=60)
                invoice_number = f"DEMO-{supplier_index:02d}-{sequence:03d}"
                amount_ht, amount_tva, amount_ttc = _invoice_amounts(amount_ttc)
                payment_date = None
                payment_method = None
                attachment_path = None if (supplier_index + sequence) % 3 == 0 else _demo_attachment(invoice_number)

                if status == STATUS_PAID:
                    payment_date_value = min(today - timedelta(days=2), reception_date + timedelta(days=14 + sequence * 3))
                    payment_date = payment_date_value.isoformat()
                    payment_method = payment_methods[(supplier_index + sequence) % len(payment_methods)]

                invoice = Invoice(
                    supplier_id=supplier.id,
                    invoice_number=invoice_number,
                    invoice_date=invoice_date.isoformat(),
                    reception_date=reception_date.isoformat(),
                    due_date=due_date.isoformat(),
                    amount_ht=amount_ht,
                    tva_rate=20,
                    amount_tva=amount_tva,
                    amount_ttc=amount_ttc,
                    status=status,
                    payment_date=payment_date,
                    payment_method=payment_method,
                    attachment_path=attachment_path,
                    notes=f"{DEMO_MARKER} Facture de démonstration.",
                    created_by=admin_id,
                )
                session.add(invoice)
                session.flush()
                counts["invoices"] = int(counts["invoices"]) + 1

                if status == STATUS_PAID and payment_date and payment_method:
                    session.add(
                        Payment(
                            invoice_id=invoice.id,
                            amount=amount_ttc,
                            payment_date=payment_date,
                            payment_method=payment_method,
                            reference=f"DEMO-PAY-{supplier_index:02d}-{sequence:03d}",
                            notes=f"{DEMO_MARKER} Paiement complet de démonstration.",
                        )
                    )
                    counts["payments"] = int(counts["payments"]) + 1
                elif status == STATUS_PARTIAL:
                    partial_ratio = 0.35 + (supplier_index % 4) * 0.08
                    partial_amount = _money(amount_ttc * partial_ratio)
                    partial_date = min(today - timedelta(days=4), reception_date + timedelta(days=22))
                    session.add(
                        Payment(
                            invoice_id=invoice.id,
                            amount=partial_amount,
                            payment_date=partial_date.isoformat(),
                            payment_method=payment_methods[(supplier_index + 2) % len(payment_methods)],
                            reference=f"DEMO-PART-{supplier_index:02d}-{sequence:03d}",
                            notes=f"{DEMO_MARKER} Acompte partiel de démonstration.",
                        )
                    )
                    counts["payments"] = int(counts["payments"]) + 1

        log_templates = [
            ("Login", "user", admin_id, "Connexion administrateur de démonstration"),
            ("Add supplier", "supplier", created_suppliers[0].id, "Création fournisseur Casa Profil Aluminium"),
            ("Add supplier", "supplier", created_suppliers[4].id, "Création fournisseur Rabat Verre et Profiles"),
            ("Add invoice", "invoice", None, "Saisie facture fournisseur"),
            ("Add invoice", "invoice", None, "Saisie facture critique"),
            ("Mark invoice as paid", "invoice", None, "Règlement complet par virement"),
            ("Add payment", "invoice", None, "Acompte sur facture partielle"),
            ("Export report", "report", None, "Export du rapport des impayés"),
            ("Export Excel", "report", None, "Export Excel tableau fournisseurs"),
            ("Create backup", "database", None, "Sauvegarde de la base de données"),
            ("Login", "user", admin_id, "Connexion comptabilité"),
            ("Add invoice", "invoice", None, "Saisie facture accessoire aluminium"),
        ]
        first_invoice = session.query(Invoice).filter(_demo_invoice_filter()).order_by(Invoice.id.asc()).first()
        paid_invoice = session.query(Invoice).filter(_demo_invoice_filter(), Invoice.status == STATUS_PAID).first()
        partial_invoice = session.query(Invoice).filter(_demo_invoice_filter(), Invoice.status == STATUS_PARTIAL).first()
        invoice_lookup = {
            "Add invoice": first_invoice.id if first_invoice else None,
            "Mark invoice as paid": paid_invoice.id if paid_invoice else None,
            "Add payment": partial_invoice.id if partial_invoice else None,
        }
        for offset, (action, entity_type, entity_id, detail) in enumerate(log_templates):
            if entity_type == "invoice" and entity_id is None:
                entity_id = invoice_lookup.get(action, first_invoice.id if first_invoice else None)
            session.add(
                ActivityLog(
                    user_id=admin_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    details=f"{DEMO_MARKER} {detail}",
                    created_at=datetime.combine(today - timedelta(days=offset), time(9 + offset % 8, 15)).isoformat(timespec="seconds"),
                )
            )
            counts["activity_logs"] = int(counts["activity_logs"]) + 1
    return counts


def seed_sample_data() -> None:
    """Backward compatible optional helper for tests. It is never called automatically."""
    seed_demo_data()


def _confirm(message: str, assume_yes: bool = False) -> bool:
    if assume_yes:
        return True
    print(message)
    answer = input("Tapez DEMO pour confirmer : ").strip()
    return answer == "DEMO"


def _print_summary(title: str, summary: dict[str, int | bool]) -> None:
    print(title)
    for key, value in summary.items():
        print(f"- {key}: {value}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed de données de démonstration PLAST ALUM.")
    parser.add_argument("--demo", action="store_true", help="Insérer les données de démonstration si elles n'existent pas déjà.")
    parser.add_argument("--reset-demo", action="store_true", help="Supprimer puis réinsérer uniquement les données de démonstration.")
    parser.add_argument("--remove-demo", action="store_true", help="Supprimer uniquement les données de démonstration.")
    parser.add_argument("--yes", action="store_true", help="Confirmer automatiquement les actions de reset/suppression.")
    args = parser.parse_args(argv)

    from app.database.migrations import initialize_database

    initialize_database()
    seed_defaults()
    print(f"Base SQLite : {DATABASE_PATH}")

    if args.remove_demo:
        if not _confirm("Suppression des données marquées comme démo uniquement.", args.yes):
            print("Opération annulée.")
            return 1
        _print_summary("Données de démonstration supprimées :", remove_demo_data())
        return 0

    if args.reset_demo:
        if not _confirm("Réinitialisation des données de démonstration uniquement.", args.yes):
            print("Opération annulée.")
            return 1
        _print_summary("Données de démonstration réinitialisées :", seed_demo_data(reset=True))
        return 0

    summary = seed_demo_data(reset=False)
    if not summary.get("created"):
        print("Les données de démonstration existent déjà. Aucun doublon n'a été ajouté.")
        print("Utilisez --reset-demo pour les régénérer ou --remove-demo pour les supprimer.")
        return 0
    _print_summary("Données de démonstration insérées :", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
