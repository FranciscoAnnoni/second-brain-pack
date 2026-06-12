#!/usr/bin/env bash
# Second Brain Pack — Bootstrap para Mac
#
# Desde el repo clonado:   bash bootstrap/mac.sh
# One-liner:               /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/FranciscoAnnoni/second-brain-pack/main/bootstrap/mac.sh)"

set -uo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

REPO_URL="https://github.com/FranciscoAnnoni/second-brain-pack.git"
INSTALL_CACHE="$HOME/.cache/second-brain-pack"

echo -e "${BOLD}Second Brain Pack — Bootstrap${RESET}"
echo ""

# ── 0. Encontrar o descargar el repo ─────────────────────────────────────────
# Detectar si estamos dentro del repo (corrido con bash bootstrap/mac.sh)
if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
    _DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
    _CANDIDATE="$(cd "$_DIR/.." 2>/dev/null && pwd)"
else
    _CANDIDATE=""
fi

if [[ -d "${_CANDIDATE}/template" ]]; then
    REPO_ROOT="$_CANDIDATE"
else
    # Corrido via curl o fuera del repo — clonar/actualizar
    echo "  Descargando second-brain-pack..."
    if [[ -d "$INSTALL_CACHE/.git" ]]; then
        git -C "$INSTALL_CACHE" pull --quiet 2>/dev/null || true
    else
        mkdir -p "$(dirname "$INSTALL_CACHE")"
        git clone --quiet "$REPO_URL" "$INSTALL_CACHE"
    fi
    REPO_ROOT="$INSTALL_CACHE"
    echo -e "${GREEN}✓${RESET} Repo listo en $INSTALL_CACHE"
fi

echo "  Repo: $REPO_ROOT"
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
    echo "  Despues de instalar, volvé a correr este script."
    exit 1
fi

echo -e "${GREEN}✓${RESET} Python: $($PYTHON --version)"

# ── 2. Verificar tkinter ──────────────────────────────────────────────────
if ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
    echo -e "${YELLOW}!${RESET} tkinter no disponible en este Python."
    echo ""
    echo "  Soluciones:"
    echo "  · brew install python-tk"
    echo "  · O instala Python desde https://www.python.org/downloads/"
    echo "    (incluye tkinter por defecto)"
    exit 1
fi

echo -e "${GREEN}✓${RESET} tkinter OK"

# ── 3. Instalar customtkinter ─────────────────────────────────────────────
echo "  Instalando customtkinter..."
"$PYTHON" -m pip install customtkinter --quiet --disable-pip-version-check
echo -e "${GREEN}✓${RESET} customtkinter OK"
echo ""

# ── 4. Lanzar instalador GUI ──────────────────────────────────────────────
echo "  Abriendo instalador..."
"$PYTHON" "$REPO_ROOT/install.py"
