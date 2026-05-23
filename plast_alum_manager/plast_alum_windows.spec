# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path


project_dir = Path(SPECPATH)
app_name = "PLAST ALUM - Gestion des Paiements Fournisseurs"
entry_file = project_dir / "main.py"
icon_file = project_dir / "app" / "assets" / "icons" / "app.ico"

datas = [
    (str(project_dir / "config.py"), "."),
    (str(project_dir / "app" / "assets"), "app/assets"),
    (str(project_dir / "app" / "styles" / "dark.qss"), "app/styles"),
    (str(project_dir / "app" / "styles" / "light.qss"), "app/styles"),
    (str(project_dir / "app" / "translations" / "fr.json"), "app/translations"),
    (str(project_dir / "app" / "translations" / "ar.json"), "app/translations"),
]

hiddenimports = [
    "matplotlib.backends.backend_qtagg",
    "app.models.user_model",
    "app.models.convention_model",
    "app.models.supplier_model",
    "app.models.invoice_model",
    "app.models.payment_model",
    "app.models.log_model",
    "app.models.setting_model",
]

a = Analysis(
    [str(entry_file)],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_file) if icon_file.exists() else None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)
