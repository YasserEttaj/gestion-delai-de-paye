# TheCrownVibe - Gestion des Paiements Fournisseurs

A PyQt6 desktop application for managing supplier invoices, payments, payment deadlines, conventions, reports, notifications, backups, and local users.

The project is built for a local Windows workflow with a SQLite database and optional PyInstaller packaging.

## Features

- Supplier management with ICE, IF, RC, contact, RIB, city, email, phone, and notes.
- Invoice management with supplier links, invoice dates, reception dates, due dates, HT/TVA/TTC amounts, status, notes, and attachments.
- Payment tracking for unpaid, partially paid, and paid invoices.
- Deadline calculations with configurable warning levels.
- Convention tracking with start dates, deadline days, due dates, remaining days, status, Excel export, and PDF export.
- Dashboard metrics for suppliers, invoices, paid amounts, unpaid amounts, urgent invoices, and conventions.
- In-app notifications for invoice deadlines, missing attachments, high unpaid amounts, supplier summaries, and conventions.
- Optional desktop notifications through the system tray.
- Excel import for invoice data and Excel export for reports.
- PDF report generation.
- Activity logs with filtering and export.
- User management with admin and standard user roles.
- Dark and light themes.
- French and Arabic translation resources.
- SQLite migrations, backup, and restore.
- Windows executable build script and PyInstaller spec.

## Requirements

- Python 3.11 or newer
- Windows is recommended for the packaged executable
- The Python packages listed in `requirements.txt`

Main dependencies:

- `PyQt6`
- `SQLAlchemy`
- `bcrypt`
- `openpyxl`
- `reportlab`
- `matplotlib`
- `python-dateutil`
- `Pillow`
- `pyinstaller`

## Quick Start

From the repository root:

```powershell
cd plast_alum_manager
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

You can also start the app from the repository root with:

```powershell
python main.py
```

The root `main.py` adds `plast_alum_manager` to `sys.path` and runs the app entry point.

## Default Login

On first launch, the app creates a local admin account if no admin user exists.

| Field | Value |
| --- | --- |
| Username | `admin` |
| Email | `admin@thecrownvibe.local` |
| Password | `admin123` |
| Role | `admin` |

Change the default password after the first login from the user management area.

## Demo Data

Demo data is optional and marked so it can be removed safely.

Create or update demo data:

```powershell
python seed_demo.py
```

Equivalent module command:

```powershell
python -m app.database.seed --demo
```

Reset only demo data:

```powershell
python seed_demo.py --reset-demo --yes
```

Remove only demo data:

```powershell
python seed_demo.py --remove-demo --yes
```

The demo seed includes Moroccan suppliers, invoices, payments, PDF attachments, activity logs, and sample conventions.

## Runtime Data

The app creates runtime folders automatically:

```text
data/
  database.sqlite
  backups/
  exports/
  uploads/
  assets/
```

- `database.sqlite` stores the local SQLite database.
- `backups/` stores database backups.
- `exports/` stores generated Excel and PDF files.
- `uploads/` stores copied invoice attachments.
- `assets/` stores user-provided assets such as a custom logo.

When packaged with PyInstaller, the same `data` folder is kept beside the executable.

## Project Structure

```text
plast_alum_manager/
  main.py                         Application entry point
  config.py                       Paths, app settings, roles, statuses
  requirements.txt                Python dependencies
  seed_demo.py                    Demo data command wrapper
  build_windows.bat               Windows build script
  create_desktop_shortcut.py      Desktop shortcut helper
  the_crown_vibe_windows.spec     PyInstaller configuration

  app/
    login_window.py               Login and registration UI
    main_window.py                Main shell, navigation, notifications

    database/
      db.py                       SQLAlchemy engine/session setup
      migrations.py               SQLite table creation and migrations
      seed.py                     Defaults and demo data

    models/
      user_model.py               Users and roles
      supplier_model.py           Suppliers
      invoice_model.py            Invoices
      payment_model.py            Payments
      convention_model.py         Conventions
      notification_state_model.py Notification state
      log_model.py                Activity logs
      setting_model.py            Settings

    services/
      auth_service.py             Authentication and permissions
      supplier_service.py         Supplier business logic
      invoice_service.py          Invoice and payment business logic
      convention_service.py       Convention deadlines and exports
      notification_service.py     Alert aggregation and delivery state
      deadline_service.py         Invoice deadline categories
      report_service.py           Report data aggregation
      excel_service.py            Excel import and export
      pdf_service.py              PDF report generation
      backup_service.py           Database backup and restore
      settings_service.py         App settings
      translation_service.py      UI translations
      activity_service.py         Activity log queries
      user_service.py             User CRUD

    ui/
      pages/                      Main application pages
      widgets/                    Reusable UI widgets
      icons.py                    Icon definitions

    styles/
      themes.py                   Theme application logic
      dark.qss                    Dark stylesheet
      light.qss                   Light stylesheet

    translations/
      fr.json                     French translations
      ar.json                     Arabic translations

    assets/
      icons/                      App icons
      images/                     App images
```

## Configuration

Default settings live in `config.py`.

Important defaults:

```python
APP_NAME = "TheCrownVibe - Gestion des Paiements Fournisseurs"
COMPANY_NAME = "TheCrownVibe"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
```

Application settings are also stored in the SQLite database and can be edited from the Settings page. These include language, theme, currency, deadline thresholds, backup folder, notification behavior, and high unpaid amount threshold.

## Permissions

The app currently uses two normalized roles:

- `admin`: can manage users, edit/delete records, import/export, and manage conventions.
- `user`: standard access with restricted administrative actions.

Legacy roles are migrated to the normalized roles during database initialization.

## Build Windows Executable

From `plast_alum_manager`:

```powershell
python -m pip install -r requirements.txt
.\build_windows.bat
```

The executable is created at:

```text
dist/TheCrownVibe - Gestion des Paiements Fournisseurs/TheCrownVibe - Gestion des Paiements Fournisseurs.exe
```

Advanced PyInstaller build:

```powershell
python -m PyInstaller --noconfirm --clean the_crown_vibe_windows.spec
```

Create a desktop shortcut after building:

```powershell
python create_desktop_shortcut.py
```

Preview the shortcut action without creating it:

```powershell
python create_desktop_shortcut.py --dry-run
```

If Windows keeps showing an old icon after rebuilding:

```powershell
powershell -ExecutionPolicy Bypass -File .\refresh_icon_cache.ps1
```

## Common Workflows

Run the app:

```powershell
python main.py
```

Install or refresh dependencies:

```powershell
python -m pip install --upgrade -r requirements.txt
```

Reset the local database:

```powershell
Remove-Item .\data\database.sqlite
python main.py
```

Only delete the database when you intentionally want to lose local data or you have a backup.

## Troubleshooting

If the application does not start:

- Confirm that the virtual environment is active.
- Reinstall dependencies from `requirements.txt`.
- Check that `data/` is writable.
- Delete `data/database.sqlite` only if you want a fresh local database.

If exports fail:

- Check that `data/exports/` is writable.
- Make sure `openpyxl` and `reportlab` are installed.

If attachments do not open:

- Confirm the original file exists before adding it.
- Supported attachment formats are PDF, JPG, JPEG, and PNG.

If the packaged app has stale data:

- Check the `data` folder beside the executable.
- The build script preserves existing packaged data when possible.

## Notes

This is an internal desktop application. Keep generated runtime data, local databases, backups, uploaded files, and PyInstaller output out of source control unless there is a specific reason to archive them.
