from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


APP_NAME = "TheCrownVibe - Gestion des Paiements Fournisseurs"
SHORTCUT_NAME = "TheCrownVibe - Gestion des Paiements"


def default_exe_path(project_dir: Path) -> Path:
    return project_dir / "dist" / APP_NAME / f"{APP_NAME}.exe"


def default_icon_path(project_dir: Path) -> Path:
    dist_icon = project_dir / "dist" / APP_NAME / "_internal" / "app" / "assets" / "icons" / "app.ico"
    if dist_icon.exists():
        return dist_icon
    return project_dir / "app" / "assets" / "icons" / "app.ico"


def icon_path_for_exe(project_dir: Path, exe_path: Path) -> Path:
    exe_icon = exe_path.parent / "_internal" / "app" / "assets" / "icons" / "app.ico"
    if exe_icon.exists():
        return exe_icon
    return default_icon_path(project_dir)


def find_executable(project_dir: Path, explicit_path: str | None = None) -> Path:
    if explicit_path:
        path = Path(explicit_path).expanduser().resolve()
        if path.exists():
            return path
        raise FileNotFoundError(f"Executable introuvable: {path}")

    default_path = default_exe_path(project_dir)
    if default_path.exists():
        return default_path

    matches = sorted((project_dir / "dist").glob("**/TheCrownVibe*.exe"))
    if matches:
        return matches[0]

    raise FileNotFoundError(
        "Executable introuvable. Lancez d'abord build_windows.bat, puis réessayez."
    )


def desktop_path() -> Path:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "[Environment]::GetFolderPath('Desktop')",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    desktop = Path(result.stdout.strip())
    if desktop.exists():
        return desktop

    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        fallback = Path(user_profile) / "Desktop"
        if fallback.exists():
            return fallback
    return desktop


def create_shortcut(exe_path: Path, shortcut_path: Path, icon_path: Path, dry_run: bool = False) -> None:
    if sys.platform != "win32":
        raise OSError("La création de raccourci .lnk est disponible uniquement sous Windows.")

    if dry_run:
        print(f"[DRY-RUN] Cible: {exe_path}")
        print(f"[DRY-RUN] Raccourci: {shortcut_path}")
        print(f"[DRY-RUN] Icône: {icon_path}")
        return

    env = os.environ.copy()
    env["TCV_SHORTCUT_PATH"] = str(shortcut_path)
    env["TCV_TARGET_PATH"] = str(exe_path)
    env["TCV_WORKING_DIR"] = str(exe_path.parent)
    env["TCV_ICON_PATH"] = str(icon_path)

    script = r"""
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($env:TCV_SHORTCUT_PATH)
$shortcut.TargetPath = $env:TCV_TARGET_PATH
$shortcut.WorkingDirectory = $env:TCV_WORKING_DIR
if (Test-Path -LiteralPath $env:TCV_ICON_PATH) {
    $shortcut.IconLocation = "$env:TCV_ICON_PATH,0"
} else {
    $shortcut.IconLocation = "$env:TCV_TARGET_PATH,0"
}
$shortcut.Description = "TheCrownVibe - Gestion des Paiements Fournisseurs"
$shortcut.Save()
"""
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], check=True, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Créer le raccourci bureau TheCrownVibe.")
    parser.add_argument("--exe", help="Chemin optionnel vers l'exécutable généré.")
    parser.add_argument("--dry-run", action="store_true", help="Afficher les chemins sans créer le raccourci.")
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parent
    exe_path = find_executable(project_dir, args.exe)
    shortcut_path = desktop_path() / f"{SHORTCUT_NAME}.lnk"
    icon_path = icon_path_for_exe(project_dir, exe_path)
    create_shortcut(exe_path, shortcut_path, icon_path, args.dry_run)
    if not args.dry_run:
        desktop = desktop_path()
        for legacy_name in ("Yassbyte - Gestion des Paiements", "PLAST ALUM - Gestion des Paiements"):
            legacy_shortcut = desktop / f"{legacy_name}.lnk"
            if legacy_shortcut.exists() and legacy_shortcut != shortcut_path:
                legacy_shortcut.unlink()
    if args.dry_run:
        print("[OK] Test des chemins terminé.")
    else:
        print(f"[OK] Raccourci créé: {shortcut_path}")
        print(f"[OK] Cible: {exe_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
