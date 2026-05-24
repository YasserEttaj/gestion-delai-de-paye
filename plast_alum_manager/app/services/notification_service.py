from __future__ import annotations

from datetime import datetime, time, timedelta

from app.database.db import session_scope
from app.models.notification_state_model import NotificationState
from app.services.convention_service import ConventionService
from app.services.invoice_service import InvoiceService
from app.services.settings_service import SettingsService


LEVEL_RANK = {
    "info": 0,
    "normal": 1,
    "attention": 2,
    "urgent": 3,
    "critical": 4,
}


class NotificationService:
    @staticmethod
    def _now() -> datetime:
        return datetime.now().replace(microsecond=0)

    @staticmethod
    def _iso(value: datetime | None = None) -> str:
        return (value or NotificationService._now()).isoformat(timespec="seconds")

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _truthy(value: str | None, default: bool = False) -> bool:
        if value is None:
            return default
        return str(value).strip().lower() in {"1", "true", "yes", "oui", "on"}

    @staticmethod
    def _int_setting(settings: dict[str, str], key: str, default: int, minimum: int = 1) -> int:
        try:
            return max(int(float(settings.get(key, default))), minimum)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def settings() -> dict[str, str]:
        return SettingsService.all()

    @classmethod
    def permission_state(cls) -> str:
        state = (cls.settings().get("notifications_permission") or "ask").strip().lower()
        return state if state in {"ask", "granted", "denied"} else "ask"

    @classmethod
    def set_permission(cls, granted: bool, user_id: int | None = None) -> None:
        SettingsService.set_many(
            {
                "notifications_permission": "granted" if granted else "denied",
                "desktop_notifications_enabled": "true" if granted else "false",
            },
            user_id,
        )

    @classmethod
    def desktop_enabled(cls) -> bool:
        settings = cls.settings()
        return (
            cls._truthy(settings.get("notifications_enabled"), True)
            and cls.permission_state() == "granted"
            and cls._truthy(settings.get("desktop_notifications_enabled"), False)
        )

    @classmethod
    def in_app_enabled(cls) -> bool:
        settings = cls.settings()
        return cls._truthy(settings.get("notifications_enabled"), True) and cls._truthy(settings.get("in_app_notifications_enabled"), True)

    @staticmethod
    def _source_enabled(alert: dict, settings: dict[str, str]) -> bool:
        source = alert.get("source")
        kind = alert.get("kind")
        if source == "invoice" and not NotificationService._truthy(settings.get("notify_invoices"), True):
            return False
        if source == "convention" and not NotificationService._truthy(settings.get("notify_conventions"), True):
            return False
        if kind == "missing_attachment" and not NotificationService._truthy(settings.get("notify_missing_attachments"), True):
            return False
        if kind == "high_amount" and not NotificationService._truthy(settings.get("notify_high_amounts"), True):
            return False
        if kind == "supplier_summary" and not NotificationService._truthy(settings.get("notify_supplier_summaries"), True):
            return False
        return True

    @staticmethod
    def _level_enabled(alert: dict, settings: dict[str, str]) -> bool:
        minimum = settings.get("notification_min_level", "attention")
        return LEVEL_RANK.get(alert.get("level", "info"), 0) >= LEVEL_RANK.get(minimum, LEVEL_RANK["attention"])

    @classmethod
    def source_alerts(cls) -> list[dict]:
        settings = cls.settings()
        if not cls._truthy(settings.get("notifications_enabled"), True):
            return []

        alerts = []
        if cls._truthy(settings.get("notify_invoices"), True):
            alerts.extend(InvoiceService.notifications())
        if cls._truthy(settings.get("notify_conventions"), True):
            alerts.extend(ConventionService.notifications())

        normalized = []
        for index, alert in enumerate(alerts):
            item = dict(alert)
            item.setdefault("level", "info")
            item.setdefault("source", "system")
            item.setdefault("kind", item["source"])
            item.setdefault("key", f"{item['source']}:{item['kind']}:{item.get('invoice_id') or item.get('convention_id') or index}")
            if not cls._source_enabled(item, settings):
                continue
            if not cls._level_enabled(item, settings):
                continue
            normalized.append(item)
        normalized.sort(key=lambda item: LEVEL_RANK.get(item.get("level", "info"), 0), reverse=True)
        return normalized[:100]

    @classmethod
    def _sync_states(cls, user_id: int) -> dict[str, dict]:
        alerts = {alert["key"]: alert for alert in cls.source_alerts()}
        now = cls._iso()
        with session_scope() as session:
            states = {state.alert_key: state for state in session.query(NotificationState).filter_by(user_id=user_id).all()}
            active_keys = set(alerts)
            if active_keys:
                for state in list(states.values()):
                    if state.alert_key not in active_keys:
                        session.delete(state)
                        states.pop(state.alert_key, None)
            else:
                for state in list(states.values()):
                    session.delete(state)
                return alerts

            for key, alert in alerts.items():
                state = states.get(key)
                if not state:
                    state = NotificationState(
                        user_id=user_id,
                        alert_key=key,
                        level=alert.get("level", "info"),
                        title=alert.get("title"),
                        message=alert.get("message"),
                        source=alert.get("source"),
                        updated_at=now,
                    )
                    session.add(state)
                    states[key] = state
                else:
                    state.level = alert.get("level", "info")
                    state.title = alert.get("title")
                    state.message = alert.get("message")
                    state.source = alert.get("source")
                    state.updated_at = now
        return alerts

    @classmethod
    def active_alerts(
        cls,
        user_id: int,
        *,
        include_read: bool = True,
        include_snoozed: bool = False,
        include_dismissed: bool = False,
    ) -> list[dict]:
        alerts = cls._sync_states(user_id)
        now = cls._now()
        with session_scope() as session:
            states = {state.alert_key: state for state in session.query(NotificationState).filter_by(user_id=user_id).all()}

        rows = []
        for key, alert in alerts.items():
            state = states.get(key)
            if not state:
                continue
            if state.dismissed_at and not include_dismissed:
                continue
            snoozed_until = cls._parse_datetime(state.snoozed_until)
            if snoozed_until and snoozed_until > now and not include_snoozed:
                continue
            if state.read_at and not include_read:
                continue
            row = dict(alert)
            row.update(
                {
                    "read": bool(state.read_at),
                    "read_at": state.read_at,
                    "dismissed_at": state.dismissed_at,
                    "snoozed_until": state.snoozed_until,
                    "last_delivered_at": state.last_delivered_at,
                    "delivery_count": state.delivery_count,
                }
            )
            rows.append(row)
        rows.sort(
            key=lambda item: (
                item.get("read", False),
                -LEVEL_RANK.get(item.get("level", "info"), 0),
                item.get("title", ""),
            )
        )
        return rows

    @classmethod
    def unread_count(cls, user_id: int) -> int:
        if not cls.in_app_enabled():
            return 0
        return len(cls.active_alerts(user_id, include_read=False))

    @classmethod
    def mark_read(cls, user_id: int, alert_key: str) -> None:
        cls._sync_states(user_id)
        with session_scope() as session:
            state = session.query(NotificationState).filter_by(user_id=user_id, alert_key=alert_key).first()
            if state and not state.read_at:
                state.read_at = cls._iso()

    @classmethod
    def mark_all_read(cls, user_id: int) -> None:
        cls._sync_states(user_id)
        now = cls._iso()
        with session_scope() as session:
            for state in session.query(NotificationState).filter_by(user_id=user_id).all():
                if not state.dismissed_at and not state.read_at:
                    state.read_at = now

    @classmethod
    def snooze(cls, user_id: int, alert_key: str, minutes: int | None = None) -> None:
        settings = cls.settings()
        minutes = minutes or cls._int_setting(settings, "notification_snooze_minutes", 60)
        until = cls._iso(cls._now() + timedelta(minutes=minutes))
        cls._sync_states(user_id)
        with session_scope() as session:
            state = session.query(NotificationState).filter_by(user_id=user_id, alert_key=alert_key).first()
            if state:
                state.snoozed_until = until
                state.read_at = state.read_at or cls._iso()

    @classmethod
    def dismiss(cls, user_id: int, alert_key: str) -> None:
        cls._sync_states(user_id)
        with session_scope() as session:
            state = session.query(NotificationState).filter_by(user_id=user_id, alert_key=alert_key).first()
            if state:
                now = cls._iso()
                state.dismissed_at = now
                state.read_at = state.read_at or now

    @classmethod
    def _quiet_hours_active(cls, settings: dict[str, str]) -> bool:
        if not cls._truthy(settings.get("notification_quiet_hours_enabled"), False):
            return False

        def parse_clock(value: str | None, fallback: time) -> time:
            try:
                hour, minute = [int(part) for part in (value or "").split(":", 1)]
                return time(hour, minute)
            except (TypeError, ValueError):
                return fallback

        start = parse_clock(settings.get("notification_quiet_start"), time(22, 0))
        end = parse_clock(settings.get("notification_quiet_end"), time(7, 0))
        current = datetime.now().time()
        if start <= end:
            return start <= current < end
        return current >= start or current < end

    @classmethod
    def desktop_candidates(cls, user_id: int) -> list[dict]:
        settings = cls.settings()
        if not cls.desktop_enabled() or cls._quiet_hours_active(settings):
            return []
        repeat_minutes = cls._int_setting(settings, "notification_repeat_minutes", 180)
        repeat_after = cls._now() - timedelta(minutes=repeat_minutes)
        candidates = []
        for alert in cls.active_alerts(user_id, include_read=False):
            last_delivered = cls._parse_datetime(alert.get("last_delivered_at"))
            if last_delivered and last_delivered > repeat_after:
                continue
            candidates.append(alert)
        return candidates[:3]

    @classmethod
    def record_delivered(cls, user_id: int, alert_key: str) -> None:
        cls._sync_states(user_id)
        with session_scope() as session:
            state = session.query(NotificationState).filter_by(user_id=user_id, alert_key=alert_key).first()
            if state:
                state.last_delivered_at = cls._iso()
                state.delivery_count = int(state.delivery_count or 0) + 1
