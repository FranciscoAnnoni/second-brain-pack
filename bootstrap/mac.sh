#!/usr/bin/env bash
# Second Brain Pack — Bootstrap para Mac
# Uso: bash bootstrap/mac.sh

set -uo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BOLD}Second Brain Pack — Bootstrap${RESET}"
echo ""

# ── 1. Verificar Python 3.8+ ──────────────────────────────────────────────
PYTHON=""
for py in python3 python; do
    if command -v "$py" &>/dev/null; then
        ok=$("$py" -c "import sys; print(sys.version_info >= (3, 8))" 2>/dev/null)
        if [[ "$ok" == "True" ]]; then
            PYTHON="$py"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    echo -e "${RED}✗${RESET} Python 3.8+ no encontrado."
    echo ""
    echo "  Opciones:"
    echo "  · Homebrew:    brew install python"
    echo "  · Python.org:  https://www.python.org/downloads/"
    echo ""
    echo "  Despues de instalar, volvé a correr:"
    echo "  bash bootstrap/mac.sh"
    exit 1
fi

echo -e "${GREEN}✓${RESET} Python: $($PYTHON --version)"

# ── 2. Verificar tkinter (necesario para la GUI) ──────────────────────────
if ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
    echo -e "${YELLOW}!${RESET} tkinter no disponible en este Python."
    echo ""
    echo "  tkinter viene incluido con Python.org pero no siempre con brew."
    echo ""
    echo "  Soluciones:"
    echo "  · brew install python-tk"
    echo "  · O usa el Python de python.org"
    exit 1
fi

echo -e "${GREEN}✓${RESET} tkinter OK"

# ── 3. Instalar customtkinter ─────────────────────────────────────────────
echo "  Instalando customtkinter (si no esta)..."
"$PYTHON" -m pip install customtkinter --quiet --disable-pip-version-check

echo -e "${GREEN}✓${RESET} customtkinter OK"
echo ""

# ── 4. Lanzar instalador ──────────────────────────────────────────────────
echo "  Abriendo instalador..."
"$PYTHON" "$REPO_ROOT/install.py"
