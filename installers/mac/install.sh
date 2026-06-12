#!/usr/bin/env bash
# Second Brain Pack — Mac Installer
# Requires: macOS, bash 3.2+

set -uo pipefail

# ── Colors ─────────────────────────────────────────────────────────────────
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
DIM='\033[2m'
RESET='\033[0m'

ok()   { echo -e "${GREEN}✓${RESET} $*"; }
info() { echo -e "${CYAN}→${RESET} $*"; }
warn() { echo -e "${YELLOW}!${RESET} $*"; }
err()  { echo -e "${RED}✗${RESET} $*" >&2; }
ask()  { echo -e "${BOLD}$*${RESET}"; }

# ── Paths ───────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(cd "$SCRIPT_DIR/../../template" && pwd)"

if [[ ! -d "$TEMPLATE_DIR" ]]; then
    err "No se encontro el directorio template/ en $TEMPLATE_DIR"
    err "Asegurate de correr este script desde dentro del repo second-brain-pack."
    exit 1
fi

# ── Welcome ─────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}Second Brain Pack — Instalador Mac${RESET}"
echo -e "${DIM}Configura tu segundo cerebro con IA en menos de 10 minutos.${RESET}"
echo ""

# ── Step 1: Agent ────────────────────────────────────────────────────────────
ask "Que agente de IA usas?"
echo "  [1] Gemini CLI  (gratuito, recomendado para empezar)"
echo "  [2] Claude Code (pago, mas capacidades)"
echo "  [3] Otro"
echo "  [0] No tengo ninguno"
echo ""
read -rp "Elegí una opcion [1]: " agent_choice
agent_choice="${agent_choice:-1}"

case "$agent_choice" in
    1)
        AGENT="gemini"
        AGENT_CMD=""
        if ! command -v gemini &>/dev/null; then
            warn "Gemini CLI no esta instalado."
            echo ""
            echo "  Instalalo con:"
            echo "  npm install -g @google/gemini-cli"
            echo ""
            read -rp "Continuar igual (podras instalarlo despues)? [s/N]: " cont
            [[ "${cont:-n}" =~ ^[sS]$ ]] || exit 0
        else
            ok "Gemini CLI detectado: $(gemini --version 2>/dev/null | head -1)"
        fi
        ;;
    2)
        AGENT="claude"
        AGENT_CMD=""
        if ! command -v claude &>/dev/null; then
            warn "Claude Code no esta instalado."
            echo ""
            echo "  Instalalo con:"
            echo "  npm install -g @anthropic-ai/claude-code"
            echo ""
            read -rp "Continuar igual (podras instalarlo despues)? [s/N]: " cont
            [[ "${cont:-n}" =~ ^[sS]$ ]] || exit 0
        else
            ok "Claude Code detectado: $(claude --version 2>/dev/null | head -1)"
        fi
        ;;
    3)
        AGENT="other"
        echo ""
        read -rp "Comando del agente (ej: 'llm'): " AGENT_CMD
        if [[ -z "$AGENT_CMD" ]]; then
            err "Necesitas ingresar un comando."
            exit 1
        fi
        ;;
    0)
        echo ""
        info "Instala Gemini CLI (gratuito):"
        echo "  npm install -g @google/gemini-cli"
        echo ""
        info "Luego volvé a correr este instalador."
        exit 0
        ;;
    *)
        err "Opcion invalida."
        exit 1
        ;;
esac

echo ""

# ── Step 2: Language ──────────────────────────────────────────────────────────
ask "Idioma del brief?"
echo "  [1] Espanol (por defecto)"
echo "  [2] English"
echo ""
read -rp "Elegí una opcion [1]: " lang_choice
lang_choice="${lang_choice:-1}"

case "$lang_choice" in
    2) LANG_CODE="en" ;;
    *) LANG_CODE="es" ;;
esac

echo ""

# ── Step 3: Agent name + user name ───────────────────────────────────────────
ask "Como queres llamar a tu agente de IA?"
read -rp "Nombre del agente [Aria]: " AGENT_NAME
AGENT_NAME="${AGENT_NAME:-Aria}"

ask "Como te llamas vos?"
read -rp "Tu nombre: " USER_NAME
if [[ -z "$USER_NAME" ]]; then
    USER_NAME="$(whoami)"
fi

echo ""

# ── Step 4: Context size ──────────────────────────────────────────────────────
ask "Cuanto contexto le das al agente?"
echo "  [1] Compact  — menos tokens, mejor para Gemini free (~500 tokens)"
echo "  [2] Standard — mas contexto, mejor para Claude Code (~1500 tokens)"
echo ""

if [[ "$AGENT" == "gemini" ]]; then
    read -rp "Elegí una opcion [1]: " ctx_choice
    ctx_choice="${ctx_choice:-1}"
else
    read -rp "Elegí una opcion [2]: " ctx_choice
    ctx_choice="${ctx_choice:-2}"
fi

case "$ctx_choice" in
    2) CONTEXT_SIZE="standard" ;;
    *) CONTEXT_SIZE="compact" ;;
esac

echo ""

# ── Step 5: Vault location ────────────────────────────────────────────────────
DEFAULT_VAULT="$HOME/SecondBrain"
ask "Donde crear el vault?"
read -rp "Ruta [${DEFAULT_VAULT}]: " VAULT_PATH
VAULT_PATH="${VAULT_PATH:-$DEFAULT_VAULT}"
# Expand ~ if user typed it
VAULT_PATH="${VAULT_PATH/#\~/$HOME}"

if [[ -d "$VAULT_PATH" ]] && [[ -n "$(ls -A "$VAULT_PATH" 2>/dev/null)" ]]; then
    warn "Ya existe algo en $VAULT_PATH"
    read -rp "Continuar e instalar encima? [s/N]: " overwrite
    [[ "${overwrite:-n}" =~ ^[sS]$ ]] || exit 0
fi

echo ""

# ── Step 6: Obsidian (Claude only) ───────────────────────────────────────────
OBSIDIAN="false"
if [[ "$AGENT" == "claude" ]]; then
    ask "Tenes Obsidian instalado y queres abrir el vault en el?"
    read -rp "[s/N]: " obs_choice
    if [[ "${obs_choice:-n}" =~ ^[sS]$ ]]; then
        OBSIDIAN="true"
    fi
    echo ""
fi

# ── Step 7: Check Python ──────────────────────────────────────────────────────
info "Verificando dependencias..."

PYTHON=""
for py in python3 python; do
    if command -v "$py" &>/dev/null; then
        version=$("$py" -c "import sys; print(sys.version_info[:2] >= (3,8))" 2>/dev/null)
        if [[ "$version" == "True" ]]; then
            PYTHON="$py"
            ok "Python: $($py --version)"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    err "Python 3.8+ es requerido para brief.py"
    echo ""
    echo "  Instalalo con Homebrew:"
    echo "  brew install python"
    echo ""
    echo "  O descargalo en: https://www.python.org/downloads/"
    exit 1
fi

# ── Step 8: Copy template ─────────────────────────────────────────────────────
info "Creando vault en $VAULT_PATH ..."

mkdir -p "$VAULT_PATH"
cp -r "$TEMPLATE_DIR/." "$VAULT_PATH/"

# Remove installer artifacts not needed in the user's vault
rm -f "$VAULT_PATH/config/agent.yaml.example"

# Copy correct SOUL.md variant
cp "$VAULT_PATH/variants/soul-${CONTEXT_SIZE}.md" "$VAULT_PATH/SOUL.md"

# Copy correct MEMORY.md variant
cp "$VAULT_PATH/variants/memory-${CONTEXT_SIZE}.md" "$VAULT_PATH/MEMORY.md"

# Remove variants folder (not needed in user's vault)
rm -rf "$VAULT_PATH/variants"

ok "Archivos copiados"

# ── Step 9: Replace placeholders in SOUL.md ──────────────────────────────────
sed -i '' \
    -e "s/{{AGENT_NAME}}/${AGENT_NAME}/g" \
    -e "s/{{USER_NAME}}/${USER_NAME}/g" \
    -e "s/{{LANGUAGE}}/${LANG_CODE}/g" \
    "$VAULT_PATH/SOUL.md"

ok "SOUL.md configurado para ${AGENT_NAME}"

# ── Step 10: Write config/agent.yaml ─────────────────────────────────────────
cat > "$VAULT_PATH/config/agent.yaml" << EOF
# Second Brain — Agent Configuration
# Generated by install.sh on $(date +%Y-%m-%d)

agent: ${AGENT}
agent_command: "${AGENT_CMD}"
language: ${LANG_CODE}
agent_name: "${AGENT_NAME}"
user_name: "${USER_NAME}"
vault_path: "${VAULT_PATH}"
obsidian: ${OBSIDIAN}
context_size: ${CONTEXT_SIZE}
EOF

ok "config/agent.yaml escrito"

# ── Step 11: Install sequential-thinking MCP (optional) ──────────────────────
echo ""
ask "Instalar MCP sequential-thinking? (mejora la calidad del razonamiento)"
echo "  Requiere Node.js / npm instalado."
read -rp "[s/N]: " mcp_choice

if [[ "${mcp_choice:-n}" =~ ^[sS]$ ]]; then
    if ! command -v npm &>/dev/null; then
        warn "npm no esta instalado. Instala Node.js primero:"
        echo "  brew install node"
        echo "  O: https://nodejs.org"
        warn "MCP sequential-thinking no instalado. Podes hacerlo manualmente despues."
    else
        info "Instalando @modelcontextprotocol/server-sequential-thinking ..."
        MCP_DIR="$VAULT_PATH/.mcp/sequential-thinking"
        mkdir -p "$MCP_DIR"
        cd "$MCP_DIR"
        npm install @modelcontextprotocol/server-sequential-thinking --silent 2>/dev/null
        cd - > /dev/null

        MCP_BINARY="$MCP_DIR/node_modules/.bin/mcp-server-sequential-thinking"

        if [[ "$AGENT" == "claude" ]]; then
            mkdir -p "$VAULT_PATH/.claude"
            SETTINGS="$VAULT_PATH/.claude/settings.json"
            if [[ ! -f "$SETTINGS" ]]; then
                echo '{}' > "$SETTINGS"
            fi
            # Inject MCP config into settings.json using Python (no jq dependency)
            $PYTHON - << PYEOF
import json, sys
path = "$SETTINGS"
with open(path) as f:
    cfg = json.load(f)
cfg.setdefault("mcpServers", {})["sequential-thinking"] = {
    "command": "node",
    "args": ["$MCP_BINARY"]
}
with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
PYEOF
            ok "MCP sequential-thinking configurado en .claude/settings.json"
        else
            ok "MCP instalado en .mcp/sequential-thinking/"
            info "Para configurarlo con tu agente, revisá la documentacion de $AGENT."
        fi
    fi
fi

# ── Step 12: Obsidian vault open ──────────────────────────────────────────────
if [[ "$OBSIDIAN" == "true" ]]; then
    VAULT_NAME="$(basename "$VAULT_PATH")"
    ENCODED_PATH=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$VAULT_PATH'))")
    open "obsidian://open?vault=${VAULT_NAME}&path=${ENCODED_PATH}" 2>/dev/null || true
fi

# ── Step 13: Add `brief` alias ────────────────────────────────────────────────
echo ""
info "Agregando alias 'brief' a tu shell..."

ALIAS_LINE="alias brief='cd ${VAULT_PATH} && ${PYTHON} brief.py'"

# Detect shell config file
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_RC="$HOME/.bash_profile"
else
    SHELL_RC="$HOME/.zshrc"
fi

if grep -q "alias brief=" "$SHELL_RC" 2>/dev/null; then
    # Update existing alias
    sed -i '' "s|alias brief=.*|${ALIAS_LINE}|" "$SHELL_RC"
    ok "Alias 'brief' actualizado en $SHELL_RC"
else
    echo "" >> "$SHELL_RC"
    echo "# Second Brain" >> "$SHELL_RC"
    echo "$ALIAS_LINE" >> "$SHELL_RC"
    ok "Alias 'brief' agregado a $SHELL_RC"
fi

# ── Step 14: Git init ─────────────────────────────────────────────────────────
echo ""
info "Inicializando repositorio git..."
cd "$VAULT_PATH"
git init --quiet
git add -A
git commit --quiet -m "Initial commit — Second Brain instalado"
ok "Git inicializado con primer commit"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}Listo.${RESET}"
echo ""
echo "  Vault en: ${BOLD}${VAULT_PATH}${RESET}"
echo ""
echo -e "  Abri una nueva terminal y corré: ${BOLD}brief${RESET}"
echo ""
if [[ "$AGENT" == "claude" ]]; then
    echo -e "  O desde Claude Code: abri el vault y escribí ${BOLD}/brief${RESET}"
    echo ""
fi
