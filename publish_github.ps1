$ErrorActionPreference = "Stop"

# Cambia esta URL si tu repositorio de GitHub tiene otra dirección.
$RemoteUrl = "https://github.com/gfiuws19832/Stitchrep.git"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git no está instalado o no está disponible en PATH."
}

if (-not (Test-Path ".git")) {
    git init
}
$existingRemote = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    if ($existingRemote -ne $RemoteUrl) {
        git remote set-url origin $RemoteUrl
    }
} else {
    git remote add origin $RemoteUrl
}

git branch -M main
git add .
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "Add Stitch project"
} else {
    Write-Host "No hay cambios nuevos que confirmar."
}

git push -u origin main
Write-Host "Publicación terminada." -ForegroundColor Green
