$ErrorActionPreference = "Stop"
if (-not (Test-Path "stitch.py")) { throw "Falta stitch.py" }
if (-not (Test-Path "README.md")) { throw "Falta README.md" }
if (-not (Test-Path "requirements.txt")) { throw "Falta requirements.txt" }
py -m py_compile stitch.py
py stitch.py --version
Write-Host "Estructura y sintaxis básicas verificadas." -ForegroundColor Green
