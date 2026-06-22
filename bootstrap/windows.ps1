# Second Brain Pack — Bootstrap para Windows
#
# Desde el repo clonado:
#   powershell -ExecutionPolicy Bypass -File bootstrap\windows.ps1
#
# One-liner (PowerShell):
#   iwr -useb https://raw.githubusercontent.com/FranciscoAnnoni/second-brain-pack/main/bootstrap/windows.ps1 | iex

$RepoUrl   = "https://github.com/FranciscoAnnoni/second-brain-pack.git"
$Cache     = "$env:LOCALAPPDATA\second-brain-pack"

Write-Host "Second Brain Pack - Bootstrap" -ForegroundColor White
Write-Host ""

# ── 0. Encontrar o descargar el repo ─────────────────────────────────────────
$RepoRoot = $null

if ($PSScriptRoot -and (Test-Path "$PSScriptRoot\..\template")) {
    $RepoRoot = (Resolve-Path "$PSScriptRoot\..").Path
} else {
    Write-Host "  Descargando second-brain-pack..." -ForegroundColor Cyan
    if (Test-Path "$Cache\.git") {
        git -C $Cache pull --quiet 2>$null
    } else {
        git clone --quiet $RepoUrl $Cache
    }
    $RepoRoot = $Cache
    Write-Host "✓ Repo listo en $Cache" -ForegroundColor Green
}

Write-Host "  Repo: $RepoRoot"
Write-Host ""

# ── 1. Instalar uv si no está disponible ─────────────────────────────────
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "  Instalando uv..."
    irm https://astral.sh/uv/install.ps1 | iex
}

# Hacer uv disponible en la sesión actual
$env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "x uv no pudo instalarse. Revisá tu conexión e intentá de nuevo." -ForegroundColor Red
    Read-Host "  Presiona Enter para cerrar"
    exit 1
}

Write-Host "✓ uv: $(uv --version)" -ForegroundColor Green

# ── 2. Instalar Python 3.12 via uv ───────────────────────────────────────
Write-Host "  Verificando Python 3.12..."
uv python install 3.12 --quiet
Write-Host "✓ Python 3.12 OK" -ForegroundColor Green
Write-Host ""

# ── 3. Lanzar instalador GUI ──────────────────────────────────────────────
Write-Host "  Abriendo instalador..."
& uv run --with customtkinter "$RepoRoot\install.py"
