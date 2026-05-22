from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from config import STATUS_PAID


@dataclass(frozen=True)
class DeadlineInfo:
    days: int
    category: str
    label: str
    color: str
    tooltip: str


class DeadlineService:
    DEFAULT_THRESHOLDS = {
        "normal_max_days": 40,
        "attention_min_days": 41,
        "attention_max_days": 49,
        "urgent_min_days": 50,
        "urgent_max_days": 59,
        "critical_min_days": 60,
    }

    @staticmethod
    def parse_date(value: str | None) -> date | None:
        if not value:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value[:19], fmt).date()
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None

    @classmethod
    def thresholds_from_settings(cls, settings: dict[str, str] | None = None) -> dict[str, int]:
        settings = settings or {}
        result = cls.DEFAULT_THRESHOLDS.copy()
        for key in result:
            try:
                result[key] = int(settings.get(key, result[key]))
            except (TypeError, ValueError):
                pass
        return result

    @classmethod
    def calculate(cls, invoice, settings: dict[str, str] | None = None) -> DeadlineInfo:
        start = cls.parse_date(getattr(invoice, "reception_date", None)) or cls.parse_date(getattr(invoice, "invoice_date", None)) or date.today()
        if getattr(invoice, "status", None) == STATUS_PAID:
            end = cls.parse_date(getattr(invoice, "payment_date", None)) or date.today()
        else:
            end = date.today()
        days = max((end - start).days, 0)
        thresholds = cls.thresholds_from_settings(settings)
        if days <= thresholds["normal_max_days"]:
            return DeadlineInfo(days, "normal", "Normal", "#22C55E", "0 à 40 jours")
        if thresholds["attention_min_days"] <= days <= thresholds["attention_max_days"]:
            return DeadlineInfo(days, "attention", "Attention", "#F59E0B", "41 à 49 jours")
        if thresholds["urgent_min_days"] <= days <= thresholds["urgent_max_days"]:
            return DeadlineInfo(days, "urgent", "Urgent", "#EF4444", "50 à 59 jours")
        if days >= thresholds["critical_min_days"]:
            return DeadlineInfo(days, "critical", "Critique", "#7F1D1D", "60 jours et plus")
        return DeadlineInfo(days, "attention", "Attention", "#F59E0B", "Délai à surveiller")
