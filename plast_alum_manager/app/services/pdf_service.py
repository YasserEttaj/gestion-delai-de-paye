from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.database.db import session_scope
from app.services.log_service import LogService
from config import COMPANY_NAME, EXPORT_DIR, LOGO_PATH, STATUS_LABELS_FR


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.drawRightString(805, 18, f"Page {self._pageNumber} / {page_count}")
            super().showPage()
        super().save()


class PdfService:
    @staticmethod
    def export_report(report: dict, title: str, filters: dict, generated_by: str, user_id: int | None = None) -> Path:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        path = EXPORT_DIR / f"rapport_factures_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        doc = SimpleDocTemplate(str(path), pagesize=landscape(A4), rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
        styles = getSampleStyleSheet()
        story = []
        if LOGO_PATH.exists():
            story.append(Image(str(LOGO_PATH), width=180, height=62))
            story.append(Spacer(1, 6))
        story.extend(
            [
                Paragraph(f"<b>{COMPANY_NAME}</b>", styles["Title"]),
                Paragraph(title, styles["Heading2"]),
                Paragraph(f"Exporté le {datetime.now():%d/%m/%Y %H:%M} par {generated_by}", styles["Normal"]),
                Spacer(1, 8),
                Paragraph(f"Filtres: {', '.join(f'{k}={v}' for k, v in filters.items() if v) or 'Aucun'}", styles["Normal"]),
                Spacer(1, 12),
            ]
        )
        data = [[
            "ID",
            "Fournisseur",
            "Facture",
            "Date",
            "TTC",
            "Statut",
            "Jours",
            "Délai",
            "Reste",
        ]]
        for row in report["rows"]:
            invoice = row["invoice"]
            data.append(
                [
                    invoice.id,
                    row["supplier"].name[:28],
                    invoice.invoice_number,
                    invoice.invoice_date,
                    f"{float(invoice.amount_ttc or 0):,.2f}",
                    STATUS_LABELS_FR.get(invoice.status, invoice.status),
                    row["deadline"].days,
                    row["deadline"].label,
                    f"{row['outstanding_amount']:,.2f}",
                ]
            )
        if len(data) == 1:
            data.append(["", "Aucune donnée", "", "", "", "", "", "", ""])
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Total factures: {report['count']}", styles["Normal"]))
        story.append(Paragraph(f"Montant total: {report['total_amount']:,.2f} MAD", styles["Normal"]))
        story.append(Paragraph(f"Montant impayé: {report['total_unpaid']:,.2f} MAD", styles["Normal"]))
        story.append(Spacer(1, 36))
        story.append(Paragraph("Signature: ______________________________", styles["Normal"]))
        doc.build(story, canvasmaker=NumberedCanvas)
        with session_scope() as session:
            LogService.log(session, user_id, "Export PDF", "report", None, str(path))
        return path
