from __future__ import annotations

from app.database.db import Base, engine
from config import ROLE_ADMIN, ROLE_USER


def initialize_database() -> None:
    from app.models import convention_model, invoice_model, log_model, notification_state_model, payment_model, setting_model, supplier_model, user_model  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_users_table()
    _migrate_suppliers_table()
    _migrate_invoices_table()
    _migrate_payments_table()
    _migrate_activity_logs_table()
    _migrate_settings_table()
    _migrate_conventions_table()
    _migrate_notification_states_table()


def _table_columns(table_name: str) -> set[str]:
    with engine.connect() as connection:
        rows = connection.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _migrate_users_table() -> None:
    columns = _table_columns("users")
    if not columns:
        return

    with engine.begin() as connection:
        if "phone" not in columns:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN phone VARCHAR")
        if "email" not in columns:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN email VARCHAR")
        if "role" not in columns:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user' NOT NULL")
        if "is_active" not in columns:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL")
        if "created_at" not in columns:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN created_at VARCHAR")
        if "updated_at" not in columns:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN updated_at VARCHAR")
        if "last_login" not in columns:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN last_login VARCHAR")

        connection.exec_driver_sql(
            """
            UPDATE users
            SET role = ?
            WHERE lower(role) IN ('admin', 'administrateur', 'administrator')
               OR role = 'Admin'
            """,
            (ROLE_ADMIN,),
        )
        connection.exec_driver_sql(
            """
            UPDATE users
            SET role = ?
            WHERE role IS NULL
               OR trim(role) = ''
               OR lower(role) IN ('user', 'utilisateur', 'viewer', 'accountant', 'comptable')
               OR role IN ('Viewer', 'Comptable')
            """,
            (ROLE_USER,),
        )
        connection.exec_driver_sql(
            "UPDATE users SET role = ? WHERE role NOT IN (?, ?)",
            (ROLE_USER, ROLE_ADMIN, ROLE_USER),
        )


def _add_columns(table_name: str, columns: dict[str, str]) -> None:
    existing = _table_columns(table_name)
    if not existing:
        return
    with engine.begin() as connection:
        for column, definition in columns.items():
            if column not in existing:
                connection.exec_driver_sql(f"ALTER TABLE {table_name} ADD COLUMN {column} {definition}")


def _migrate_suppliers_table() -> None:
    _add_columns(
        "suppliers",
        {
            "ice": "VARCHAR",
            "if_number": "VARCHAR",
            "rc": "VARCHAR",
            "address": "TEXT",
            "city": "VARCHAR",
            "phone": "VARCHAR",
            "email": "VARCHAR",
            "contact_person": "VARCHAR",
            "rib": "VARCHAR",
            "notes": "TEXT",
            "created_at": "VARCHAR",
            "updated_at": "VARCHAR",
        },
    )


def _migrate_invoices_table() -> None:
    _add_columns(
        "invoices",
        {
            "reception_date": "VARCHAR",
            "due_date": "VARCHAR",
            "amount_ht": "FLOAT DEFAULT 0.0 NOT NULL",
            "tva_rate": "FLOAT DEFAULT 20.0 NOT NULL",
            "amount_tva": "FLOAT DEFAULT 0.0 NOT NULL",
            "amount_ttc": "FLOAT DEFAULT 0.0 NOT NULL",
            "status": "VARCHAR DEFAULT 'unpaid' NOT NULL",
            "payment_date": "VARCHAR",
            "payment_method": "VARCHAR",
            "attachment_path": "VARCHAR",
            "notes": "TEXT",
            "created_by": "INTEGER",
            "created_at": "VARCHAR",
            "updated_at": "VARCHAR",
        },
    )


def _migrate_payments_table() -> None:
    _add_columns(
        "payments",
        {
            "reference": "VARCHAR",
            "notes": "TEXT",
            "created_at": "VARCHAR",
        },
    )


def _migrate_activity_logs_table() -> None:
    _add_columns(
        "activity_logs",
        {
            "user_id": "INTEGER",
            "action": "VARCHAR",
            "entity_type": "VARCHAR",
            "entity_id": "INTEGER",
            "details": "TEXT",
            "created_at": "VARCHAR",
        },
    )


def _migrate_settings_table() -> None:
    _add_columns(
        "settings",
        {
            "key": "VARCHAR",
            "value": "TEXT",
        },
    )


def _migrate_conventions_table() -> None:
    _add_columns(
        "conventions",
        {
            "company_name": "VARCHAR",
            "convention_number": "VARCHAR",
            "convention_type": "VARCHAR",
            "start_date": "VARCHAR",
            "deadline_days": "INTEGER DEFAULT 60 NOT NULL",
            "due_date": "VARCHAR",
            "remaining_days": "INTEGER DEFAULT 0 NOT NULL",
            "status": "VARCHAR DEFAULT 'active' NOT NULL",
            "notes": "TEXT",
            "created_at": "VARCHAR",
            "updated_at": "VARCHAR",
        },
    )


def _migrate_notification_states_table() -> None:
    _add_columns(
        "notification_states",
        {
            "user_id": "INTEGER",
            "alert_key": "VARCHAR",
            "level": "VARCHAR DEFAULT 'info' NOT NULL",
            "title": "VARCHAR",
            "message": "TEXT",
            "source": "VARCHAR",
            "read_at": "VARCHAR",
            "dismissed_at": "VARCHAR",
            "snoozed_until": "VARCHAR",
            "last_delivered_at": "VARCHAR",
            "delivery_count": "INTEGER DEFAULT 0 NOT NULL",
            "created_at": "VARCHAR",
            "updated_at": "VARCHAR",
        },
    )
