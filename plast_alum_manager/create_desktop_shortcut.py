from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


APP_NAME = "PLAST ALUM - Gestion des Paiements Fournisseurs"
SHORTCUT_NAME = "PLAST ALUM - Gestion des Paiements"


def default_exe_path(project_dir: Path) -> Path:
    return project_dir / "dist" / APP_NAME / f"{APP_NAME}.exe"


def find_executable(project_dir: Path, explicit_path: str | None = None) -> Path:
    if explicit_path:
        path = Path(explicit_path).expanduser().resolve()
        if path.exists():
            return path
        raise FileNotFoundError(f"Executable introuvable: {path}")

    default_path = default_exe_path(project_dir)
    if default_path.exists():
        return default_path

    matches = sorted((project_dir / "dist").glob("**/PLAST ALUM*.exe"))
    if matches:
        return matches[0]

    raise FileNotFoundError(
        "Executable introuvable. Lancez d'abord build_windows.bat, puis réessayez."
    )


def desktop_path() -> Path:
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        desktop = Path(user_profile) / "Desktop"
        if desktop.exists():
            return desktop

    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "[Environment]::GetFolderPath('Desktop')",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return Path(result.stdout.strip())


def create_shortcut(exe_path: Path, shortcut_path: Path, dry_run: bool = False) -> None:
    if sys.platform != "win32":
        raise OSError("La création de raccourci .lnk est disponible uniquement sous Windows.")

    if dry_run:
        print(f"[DRY-RUN] Cible: {exe_path}")
        print(f"[DRY-RUN] Raccourci: {shortcut_path}")
        return

    env = os.environ.copy()
    env["PA_SHORTCUT_PATH"] = str(shortcut_path)
    env["PA_TARGET_PATH"] = str(exe_path)
    env["PA_WORKING_DIR"] = str(exe_path.parent)

    script = r"""
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($env:PA_SHORTCUT_PATH)
$shortcut.TargetPath = $env:PA_TARGET_PATH
$shortcut.WorkingDirectory = $env:PA_WORKING_DIR
$shortcut.IconLocation = "$env:PA_TARGET_PATH,0"
$shortcut.Description = "PLAST ALUM - Gestion des Paiements Fournisseurs"
$shortcut.Save()
"""
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], check=True, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Créer le raccourci bureau PLAST ALUM.")
    parser.add_argument("--exe", help="Chemin optionnel vers l'exécutable généré.")
    parser.add_argument("--dry-run", action="store_true", help="Afficher les chemins sans créer le raccourci.")
    args = parser.parse_args()

    project_dir = Path(__file__).resolve().parent
    exe_path = find_executable(project_dir, args.exe)
    shortcut_path = desktop_path() / f"{SHORTCUT_NAME}.lnk"
    create_shortcut(exe_path, shortcut_path, args.dry_run)
    if args.dry_run:
        print("[OK] Test des chemins terminé.")
    else:
        print(f"[OK] Raccourci créé: {shortcut_path}")
        print(f"[OK] Cible: {exe_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
