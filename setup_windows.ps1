$ErrorActionPreference = "Stop"
Write-Host "== Preparando Stitch ==" -ForegroundColor Cyan

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "No se encuentra Python Launcher (py). Instala Python 3.11 o superior."
}
if (-not (Test-Path ".venv")) {
    py -3 -m venv .venv
}
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" stitch.py --version
Write-Host "Instalación terminada." -ForegroundColor Green
