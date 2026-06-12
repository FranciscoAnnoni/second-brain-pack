# Second Brain Pack — Bootstrap para Windows
# Uso: powershell -ExecutionPolicy Bypass -File bootstrap\windows.ps1

$RepoRoot = Split-Path $PSScriptRoot -Parent

Write-Host "Second Brain Pack — Bootstrap" -ForegroundColor White
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
    Write-Host "✗ Python 3.8+ no encontrado." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Opciones:"
    Write-Host "  · winget:       winget install Python.Python.3"
    Write-Host "  · Microsoft Store: buscar 'Python 3'"
    Write-Host "  · Python.org:   https://www.python.org/downloads/"
    Write-Host ""
    Write-Host "  Al instalar, marca la opcion 'Add Python to PATH'."
    Write-Host ""
    Write-Host "  Despues de instalar, volvé a correr este script."
    Read-Host "  Presiona Enter para cerrar"
    exit 1
}

$PyVersion = & $PythonCmd --version 2>&1
Write-Host "✓ $PyVersion" -ForegroundColor Green

# ── 2. Instalar customtkinter ─────────────────────────────────────────────
Write-Host "  Instalando customtkinter (si no esta)..."
& $PythonCmd -m pip install customtkinter --quiet --disable-pip-version-check
Write-Host "✓ customtkinter OK" -ForegroundColor Green
Write-Host ""

# ── 3. Lanzar instalador ──────────────────────────────────────────────────
Write-Host "  Abriendo instalador..."
& $PythonCmd "$RepoRoot\install.py"
