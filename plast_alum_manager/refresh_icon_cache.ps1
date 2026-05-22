# Refreshes Windows Explorer icon cache after replacing the app icon.
# Run from PowerShell only if the desktop/start menu still shows the old icon.

$ErrorActionPreference = "SilentlyContinue"

Write-Host "Refreshing Windows icon cache..."

$iconCache = Join-Path $env:LOCALAPPDATA "IconCache.db"
Remove-Item -LiteralPath $iconCache -Force

$explorerCacheDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Explorer"
Get-ChildItem -Path $explorerCacheDir -Filter "iconcache_*.db" | Remove-Item -Force

if (Get-Command ie4uinit.exe -ErrorAction SilentlyContinue) {
    ie4uinit.exe -show
}

Stop-Process -Name explorer -Force
Start-Sleep -Seconds 2
Start-Process explorer.exe

Write-Host "Icon cache refreshed. If a shortcut still looks old, recreate it with:"
Write-Host "python create_desktop_shortcut.py"
