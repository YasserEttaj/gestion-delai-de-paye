# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['..\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\HP\\Documents\\PLAST-ALUM\\plast_alum_manager\\config.py', '.'), ('C:\\Users\\HP\\Documents\\PLAST-ALUM\\plast_alum_manager\\app\\assets', 'app\\assets'), ('C:\\Users\\HP\\Documents\\PLAST-ALUM\\plast_alum_manager\\app\\styles\\dark.qss', 'app\\styles'), ('C:\\Users\\HP\\Documents\\PLAST-ALUM\\plast_alum_manager\\app\\styles\\light.qss', 'app\\styles'), ('C:\\Users\\HP\\Documents\\PLAST-ALUM\\plast_alum_manager\\app\\translations\\fr.json', 'app\\translations'), ('C:\\Users\\HP\\Documents\\PLAST-ALUM\\plast_alum_manager\\app\\translations\\ar.json', 'app\\translations')],
    hiddenimports=['matplotlib.backends.backend_qtagg', 'app.models.user_model', 'app.models.convention_model', 'app.models.supplier_model', 'app.models.invoice_model', 'app.models.payment_model', 'app.models.log_model', 'app.models.setting_model'],
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
    name='PLAST ALUM - Gestion des Paiements Fournisseurs',
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
    icon=['C:\\Users\\HP\\Documents\\PLAST-ALUM\\plast_alum_manager\\app\\assets\\icons\\app.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PLAST ALUM - Gestion des Paiements Fournisseurs',
)
