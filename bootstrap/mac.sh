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

# ── 1. Instalar uv si no está disponible ─────────────────────────────────
if ! command -v uv &>/dev/null; then
    echo "  Instalando uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Hacer uv disponible en la sesión actual
source "$HOME/.local/bin/env" 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"

if ! command -v uv &>/dev/null; then
    echo -e "${RED}✗${RESET} uv no pudo instalarse. Revisá tu conexión e intentá de nuevo."
    exit 1
fi

echo -e "${GREEN}✓${RESET} uv: $(uv --version)"

# ── 2. Instalar Python 3.12 via uv ───────────────────────────────────────
echo "  Verificando Python 3.12..."
uv python install 3.12 --quiet
echo -e "${GREEN}✓${RESET} Python 3.12 OK"
echo ""

# ── 3. Lanzar instalador GUI ──────────────────────────────────────────────
echo "  Abriendo instalador..."
uv run --with customtkinter "$REPO_ROOT/install.py"
