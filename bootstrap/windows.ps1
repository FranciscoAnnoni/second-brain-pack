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

# ── 1. Verificar Python 3.8+ ──────────────────────────────────────────────
$PythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $v = & $cmd -c "import sys; print(sys.version_info >= (3, 8))" 2>$null
        if ($v -eq "True") { $PythonCmd = $cmd; break }
    } catch {}
}

if (-not $PythonCmd) {
    Write-Host "x Python 3.8+ no encontrado." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Opciones:"
    Write-Host "  · winget:        winget install Python.Python.3"
    Write-Host "  · Microsoft Store: buscar 'Python 3'"
    Write-Host "  · Python.org:    https://www.python.org/downloads/"
    Write-Host ""
    Write-Host "  Al instalar, marca 'Add Python to PATH'."
    Write-Host ""
    Read-Host "  Presiona Enter para cerrar"
    exit 1
}

$PyVersion = & $PythonCmd --version 2>&1
Write-Host "✓ $PyVersion" -ForegroundColor Green

# ── 2. Instalar customtkinter ─────────────────────────────────────────────
Write-Host "  Instalando customtkinter..."
& $PythonCmd -m pip install customtkinter --quiet --disable-pip-version-check
Write-Host "✓ customtkinter OK" -ForegroundColor Green
Write-Host ""

# ── 3. Lanzar instalador GUI ──────────────────────────────────────────────
Write-Host "  Abriendo instalador..."
& $PythonCmd "$RepoRoot\install.py"
