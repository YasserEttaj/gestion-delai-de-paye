from __future__ import annotations

from app.services.invoice_service import InvoiceService
from config import STATUS_PAID


class ReportService:
    @staticmethod
    def filtered_report(filters: dict) -> dict:
        rows = InvoiceService.list_invoices(filters)
        total_amount = sum(float(row["invoice"].amount_ttc or 0) for row in rows)
        total_paid = sum(row["paid_amount"] for row in rows)
        total_unpaid = sum(row["outstanding_amount"] for row in rows if row["invoice"].status != STATUS_PAID)
        return {
            "rows": rows,
            "count": len(rows),
            "total_amount": total_amount,
            "total_paid": total_paid,
            "total_unpaid": total_unpaid,
        }

    @staticmethod
    def top_suppliers_by_unpaid(limit: int = 5) -> list[tuple[str, float]]:
        report = ReportService.filtered_report({})
        totals: dict[str, float] = {}
        for row in report["rows"]:
            if row["invoice"].status != STATUS_PAID:
                totals[row["supplier"].name] = totals.get(row["supplier"].name, 0.0) + row["outstanding_amount"]
        return sorted(totals.items(), key=lambda item: item[1], reverse=True)[:limit]
