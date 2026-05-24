@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "APP_NAME=TheCrownVibe - Gestion des Paiements Fournisseurs"
set "LEGACY_YASSBYTE_APP_NAME=Yassbyte - Gestion des Paiements Fournisseurs"
set "LEGACY_PLAST_APP_NAME=PLAST ALUM - Gestion des Paiements Fournisseurs"
set "PROJECT_DIR=%~dp0"
set "DIST_DIR=dist\%APP_NAME%"
set "DIST_DATA_DIR=%DIST_DIR%\data"
set "LEGACY_YASSBYTE_DIST_DATA_DIR=dist\%LEGACY_YASSBYTE_APP_NAME%\data"
set "LEGACY_PLAST_DIST_DATA_DIR=dist\%LEGACY_PLAST_APP_NAME%\data"
set "DATA_BACKUP_DIR=%TEMP%\tcv_build_data_%RANDOM%%RANDOM%"
set "HAS_DATA_BACKUP=0"
cd /d "%PROJECT_DIR%"

echo.
echo ==================================================
echo  Build Windows - %APP_NAME%
echo ==================================================
echo.

if exist "main.py" (
    set "ENTRY_FILE=main.py"
) else if exist "app\main.py" (
    set "ENTRY_FILE=app\main.py"
) else (
    echo [ERREUR] Fichier d'entree introuvable. main.py ou app\main.py requis.
    exit /b 1
)

echo [INFO] Fichier d'entree detecte: !ENTRY_FILE!

python -m pip show pyinstaller >nul 2>nul
if errorlevel 1 (
    echo [INFO] Installation de PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 exit /b 1
)

set "ICON_ARG="
if exist "app\assets\icons\app.ico" (
    set "ICON_ARG=--icon=%PROJECT_DIR%app\assets\icons\app.ico"
    echo [INFO] Icone detectee: app\assets\icons\app.ico
) else (
    echo [INFO] Aucune icone .ico detectee. Le build utilisera l'icone Windows par defaut.
)

set "SOURCE_DATA_DIR="
if exist "%DIST_DATA_DIR%" (
    set "SOURCE_DATA_DIR=%DIST_DATA_DIR%"
) else if exist "%LEGACY_YASSBYTE_DIST_DATA_DIR%" (
    set "SOURCE_DATA_DIR=%LEGACY_YASSBYTE_DIST_DATA_DIR%"
) else if exist "%LEGACY_PLAST_DIST_DATA_DIR%" (
    set "SOURCE_DATA_DIR=%LEGACY_PLAST_DIST_DATA_DIR%"
)

if defined SOURCE_DATA_DIR (
    echo [INFO] Conservation des donnees existantes: !SOURCE_DATA_DIR!
    mkdir "%DATA_BACKUP_DIR%" >nul 2>nul
    xcopy "!SOURCE_DATA_DIR!\*" "%DATA_BACKUP_DIR%\" /E /I /Y >nul
    if errorlevel 1 (
        echo [ERREUR] Impossible de sauvegarder temporairement les donnees existantes.
        exit /b 1
    )
    set "HAS_DATA_BACKUP=1"
)

echo [INFO] Generation de l'executable...
if not exist "%PROJECT_DIR%the_crown_vibe_windows.spec" (
    echo [ERREUR] Fichier spec introuvable: %PROJECT_DIR%the_crown_vibe_windows.spec
    exit /b 1
)

python -m PyInstaller --noconfirm "%PROJECT_DIR%the_crown_vibe_windows.spec"

if errorlevel 1 (
    echo.
    echo [ERREUR] Le build PyInstaller a echoue.
    exit /b 1
)

if not exist "%DIST_DIR%\data" mkdir "%DIST_DIR%\data"
if not exist "%DIST_DIR%\data\backups" mkdir "%DIST_DIR%\data\backups"
if not exist "%DIST_DIR%\data\exports" mkdir "%DIST_DIR%\data\exports"
if not exist "%DIST_DIR%\data\uploads" mkdir "%DIST_DIR%\data\uploads"
if not exist "%DIST_DIR%\data\assets" mkdir "%DIST_DIR%\data\assets"

if "%HAS_DATA_BACKUP%"=="1" (
    echo [INFO] Restauration des donnees existantes...
    xcopy "%DATA_BACKUP_DIR%\*" "%DIST_DIR%\data\" /E /I /Y >nul
    if errorlevel 1 (
        echo [ERREUR] Impossible de restaurer les donnees existantes.
        exit /b 1
    )
    rmdir /S /Q "%DATA_BACKUP_DIR%" >nul 2>nul
)

echo.
echo [OK] Build termine.
echo [OK] Executable:
echo      %PROJECT_DIR%%DIST_DIR%\%APP_NAME%.exe
echo.
echo Pour creer le raccourci bureau:
echo      python create_desktop_shortcut.py
echo.

endlocal
