---
phase: v2-installer
name: Instalador v2 — uv + GUI simplificada + distribución
goal: >
  Reemplazar el bootstrap con uv (sin dependencia de brew/winget/Python previo),
  simplificar la GUI a 3 preguntas, corregir bugs de brief.py, y generar
  Start.command/Start.bat como punto de entrada descargable para el usuario final.
status: Pending
---

# Plan: Instalador v2

## Contexto de decisiones

- **uv como gestor de Python** — sin brew, sin winget, solo curl (Mac) o PowerShell (Windows)
- **MCP eliminado** — era opcional y agrega fricción; removido de toda la UI y lógica
- **GUI a 3 preguntas** — agente, tu nombre, nombre del asistente. Todo lo demás son defaults
- **Obsidian** — el instalador lo instala vía brew si brew está disponible, luego abre Obsidian con instrucción clara (Camino B)
- **Claudio.app en ~/Applications** — creado localmente por el instalador = sin flag de quarantine
- **brief.py stdin** — pasar prompt por stdin en vez de argv para evitar límites de OS
- **SOUL.md en prompt** — para que Gemini conozca su identidad al correr brief desde terminal
- **Pantalla final** — 2 pasos manuales guiados: login al agente + agregar vault en Obsidian

---

## Wave 1 — Bootstrap (base de todo, sin dependencias entre sí)

### Tarea 1.1 — Reescribir `bootstrap/mac.sh` con uv

**Archivos a leer antes:** `bootstrap/mac.sh` (estado actual)

**Acción:**
Reemplazar la lógica actual por este flujo:
1. Detectar si estamos dentro del repo clonado o si hace falta clonarlo (lógica existente — mantener)
2. Verificar si `uv` está en PATH; si no, instalarlo con `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Hacer source del env de uv para que esté en PATH en la sesión actual: `source "$HOME/.local/bin/env" 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"`
4. Instalar Python 3.12 via uv si no hay Python 3.8+: `uv python install 3.12 --quiet`
5. Lanzar el instalador: `uv run --with customtkinter "$REPO_ROOT/install.py"`
6. Eliminar el paso de verificación/instalación manual de customtkinter (uv lo maneja)
7. Eliminar el paso de verificación de tkinter (python-build-standalone lo incluye)

**Criterios de aceptación:**
- `bootstrap/mac.sh` no menciona brew ni pip ni customtkinter manualmente
- Contiene `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Contiene `uv python install 3.12 --quiet`
- Contiene `uv run --with customtkinter`
- Si uv ya está instalado, no intenta reinstalarlo (`command -v uv` guard)

---

### Tarea 1.2 — Reescribir `bootstrap/windows.ps1` con uv

**Archivos a leer antes:** `bootstrap/windows.ps1` (estado actual)

**Acción:**
Reemplazar la lógica de Python por uv:
1. Detectar repo local o clonar (lógica existente — mantener)
2. Verificar si `uv` está en PATH; si no: `irm https://astral.sh/uv/install.ps1 | iex`
3. Actualizar PATH en sesión: `$env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"`
4. Instalar Python 3.12 via uv: `uv python install 3.12 --quiet`
5. Lanzar instalador: `& uv run --with customtkinter "$RepoRoot\install.py"`
6. Eliminar los pasos de instalación manual de Python y customtkinter

**Criterios de aceptación:**
- `bootstrap/windows.ps1` no tiene pasos de instalación de Python independientes
- Contiene `irm https://astral.sh/uv/install.ps1 | iex` dentro de un guard `if (-not (Get-Command uv ...))`
- Contiene `uv python install 3.12 --quiet`
- Contiene `uv run --with customtkinter`

---

### Tarea 1.3 — Crear `Start.command` y `Start.bat` en la raíz del repo

**Archivos a leer antes:** `bootstrap/mac.sh`, `bootstrap/windows.ps1`

**Acción:**
Crear dos archivos en la raíz de `/Users/FranciscoAnnoni/Proyectos/second-brain-pack/`:

`Start.command`:
```
#!/usr/bin/env bash
cd "$(dirname "$0")"
bash bootstrap/mac.sh
```
Marcar como ejecutable (chmod +x). Este archivo se puede ejecutar con doble-click en Mac (macOS lo abre en Terminal).

`Start.bat`:
```
@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File bootstrap\windows.ps1
pause
```
No requiere permisos especiales.

**Criterios de aceptación:**
- `Start.command` existe en raíz del repo, es ejecutable, contiene `bash bootstrap/mac.sh`
- `Start.bat` existe en raíz del repo, contiene `powershell -ExecutionPolicy Bypass -File bootstrap\windows.ps1`
- Ambos archivos usan `cd` al directorio del script antes de llamar al bootstrap

---

## Wave 2 — GUI simplificada (depende de Wave 1 completado)

### Tarea 2.1 — Simplificar `install.py`: quitar MCP, fusionar pantallas, 3 preguntas

**Archivos a leer antes:** `install.py` (completo)

**Acción:**

**Pantalla 1 (única pantalla de configuración):**
- Sección "Agente" con radio buttons: Gemini CLI (gratis, recomendado) / Claude Code / Otro
  - Si "Otro": campo de texto para el comando
  - Checkbox: "Instalar el agente automáticamente (requiere npm)"
- Sección "Tu asistente"
  - Campo: "¿Cómo se llama tu asistente?" (default: Aria)
  - Campo: "¿Cómo te llamás?" (obligatorio)
- Sección "Vault"
  - Campo de ruta + botón "..." para browse (default: ~/SecondBrain)
- Botón "Instalar →"

**Pantalla 2 (progreso):** igual que ahora — barra + log.

**Pantalla 3 (finalizado):** ver Tarea 2.2.

**Variables/lógica a eliminar:**
- `self.install_mcp` y toda lógica de MCP (`_configure_claude_mcp`, la sección de MCP en `_do_install`)
- `self.has_obsidian` y `self.open_obsidian_dl` como checkboxes (Obsidian pasa a ser automático — ver Tarea 2.3)
- `self.context_size` y `self.language` como preguntas explícitas (defaults: compact para Gemini, standard para Claude; idioma: 'es')
- La pantalla intermedia `show_screen_config` (fusionar en una sola pantalla)

**Variables/lógica a conservar:**
- `self.agent`, `self.install_agent`, `self.agent_name`, `self.user_name`, `self.vault_path`, `self.other_agent_cmd`
- Toda la lógica de instalación del agente CLI via npm
- `_add_brief_alias` — actualizar para usar `uv run brief.py` en vez de `python brief.py`
- `_create_mac_app` y `_create_windows_shortcut` — ver Tarea 2.3

**Criterios de aceptación:**
- `install.py` tiene exactamente 2 pantallas de usuario (config + progreso + done = 3 pantallas totales)
- No hay referencia a `mcp`, `MCP_PKG`, `install_mcp`, ni `_configure_claude_mcp`
- No hay campos para `context_size` ni `language` en la UI (son defaults internos)
- El alias `brief` usa `uv run` en lugar de ruta hardcodeada a python
- La pantalla 1 tiene exactamente los campos: agente, install_agent checkbox, agent_name, user_name, vault_path

---

### Tarea 2.2 — Pantalla final con pasos manuales guiados

**Archivos a leer antes:** `install.py` método `show_screen_done`

**Acción:**
Reemplazar `show_screen_done` para incluir:

1. Título "¡Listo!" en verde
2. Card con info del vault instalado
3. Sección "Próximos pasos" con exactamente 2 pasos:

**Paso 1 — Activar tu agente (login)**
- Texto: "Abre una nueva terminal y ejecuta: `gemini`" (o `claude` según el agente elegido)
- Subtexto: "Se abrirá el browser para iniciar sesión. Solo se hace una vez."
- Botón "Abrir Terminal" → en Mac: `osascript -e 'tell application "Terminal" to do script "gemini"' ; tell application "Terminal" to activate`; en Windows: `subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", agent_binary])`

**Paso 2 — Abrir Obsidian**
- Texto: "En Obsidian: File → Open folder as vault → seleccioná esta carpeta:"
- Muestra la ruta del vault en un label copyable
- Botón "Abrir Obsidian" → `subprocess.run(["open", "-a", "Obsidian"])` en Mac; `subprocess.Popen(["obsidian"])` en Windows

4. Botón "Abrir vault en Finder/Explorer" (ya existente)
5. Botón "Cerrar"

**Criterios de aceptación:**
- `show_screen_done` muestra exactamente 2 pasos manuales numerados
- El botón del Paso 1 abre una terminal con el comando del agente correcto según `self.agent`
- El botón del Paso 2 abre Obsidian (si está instalado) o muestra un mensaje si no
- La ruta del vault es visible en la pantalla final

---

### Tarea 2.3 — Mejorar creación de .app en Mac y shortcut en Windows

**Archivos a leer antes:** `install.py` métodos `_create_mac_app`, `_create_windows_shortcut`, `_add_brief_alias`

**Acción:**

**Mac (`_create_mac_app`):**
- Crear la `.app` en `~/Applications/` en vez de Desktop
- El script interno usa `uv run brief.py` en vez de ruta hardcodeada a Python
- También crear un alias simbólico en el Desktop apuntando a `~/Applications/{AgentName}.app`
- El `.app` debe tener un icono: copiar cualquier ícono existente en el repo, o usar el ícono de Terminal como fallback

**Windows (`_create_windows_shortcut`):**
- El `.bat` en Desktop usa `uv run brief.py` en vez de ruta al Python
- Mantener estructura actual (bat en Desktop está bien para Windows)

**`_add_brief_alias`:**
- Cambiar `alias brief='cd "{vault}" && "{python_bin}" brief.py'`
- Por: `alias brief='cd "{vault}" && uv run brief.py'`
- Windows: función PowerShell actualizada análogamente

**Criterios de aceptación:**
- `~/Applications/{agent_name}.app` creado (no en Desktop directamente)
- El script del .app ejecuta `uv run brief.py`
- El alias `brief` en .zshrc/.bash_profile usa `uv run`
- En Windows, el .bat usa `uv run brief.py`
- `_create_mac_app` no usa `python_bin` como argumento

---

## Wave 3 — Fix brief.py (independiente, puede ir en paralelo con Wave 2)

### Tarea 3.1 — brief.py: prompt por stdin en vez de argv

**Archivos a leer antes:** `template/brief.py` función `call_agent`

**Acción:**
Reemplazar en `call_agent`:
```python
# ANTES:
result = subprocess.run([binary, flag, prompt], text=True)

# DESPUÉS:
result = subprocess.run([binary, flag, "-"], input=prompt, text=True)
```
Para Gemini: el flag `-p` acepta `-` para leer de stdin (confirmado en el --help: "Appended to input on stdin (if any)").
Para Claude: `claude -p -` funciona de la misma manera.
Para "other": usar stdin también, sin el flag `-p` hardcodeado — pasar el prompt como stdin directamente: `subprocess.run([binary], input=prompt, text=True)`.

**Criterios de aceptación:**
- `call_agent` usa `input=prompt` en vez de pasar el prompt como tercer elemento de la lista de args
- Para gemini y claude: el comando es `[binary, flag, "-"]` con `input=prompt`
- Para "other": el comando es `[binary]` (o `[binary, custom_flag, "-"]` si hay flag en config) con `input=prompt`
- `brief.py` puede manejar prompts de cualquier longitud sin error de arglist

---

### Tarea 3.2 — brief.py: incluir nombre del agente en el prompt para Gemini

**Archivos a leer antes:** `template/brief.py` funciones `build_prompt`, `_build_prompt_es`, `_build_prompt_en`, `parse_config`

**Acción:**
En `build_prompt`, cuando el agente es `gemini` o `other` (no `claude`), prepend al prompt el nombre del agente y el idioma del SOUL:

```python
def build_prompt(config, pendientes, daily_date, daily_content):
    agent_name = config.get("agent_name", "Aria")
    user_name = config.get("user_name", "")
    lang = config.get("language", "es")
    agent = config.get("agent", "gemini")
    
    # Para agentes no-Claude, incluir identidad al inicio del prompt
    # (Claude lee SOUL.md automaticamente via su contexto)
    identity_prefix = ""
    if agent != "claude":
        if lang == "en":
            identity_prefix = f"You are {agent_name}, the personal AI assistant of {user_name}. Be direct, concrete, no filler. No emojis.\n\n"
        else:
            identity_prefix = f"Sos {agent_name}, el asistente personal de {user_name}. Sé directo, concreto, sin relleno. Sin emojis.\n\n"
    
    instructions = _build_prompt_es(...) if lang != "en" else _build_prompt_en(...)
    return identity_prefix + instructions
```

**Criterios de aceptación:**
- Cuando `agent == "gemini"` o `"other"`, el prompt comienza con la identidad del asistente
- Cuando `agent == "claude"`, el prompt no incluye el prefijo de identidad
- El nombre viene de `config.get("agent_name")` (configurado durante instalación)
- El comportamiento del prompt en español e inglés se mantiene

---

## Wave 4 — Distribución (depende de todo lo anterior)

### Tarea 4.1 — Actualizar README.md

**Archivos a leer antes:** `README.md`

**Acción:**
- Actualizar sección "Install on Mac" para que el primer paso sea `Start.command` (doble-click)
- Mantener el one-liner curl como alternativa
- Actualizar sección "Install on Windows" para que el primer paso sea `Start.bat` (doble-click)
- Eliminar la mención de customtkinter (ahora es transparente via uv)
- Eliminar mención de MCP sequential-thinking
- Agregar nota sobre el warning de seguridad de macOS (right-click → Abrir para Start.command)
- Actualizar la sección "Requirements" — Python ya no es un prerequisito del usuario

**Criterios de aceptación:**
- README no menciona "customtkinter" ni "MCP" ni "sequential-thinking" en instrucciones de instalación
- La sección Mac tiene `Start.command` como primera opción
- La sección Windows tiene `Start.bat` como primera opción
- Hay una nota sobre el warning de seguridad de macOS para la primera ejecución
- "Requirements" solo lista: Git, un agente (Gemini o Claude)

---

### Tarea 4.2 — Preparar GitHub Release v1.0.0

**Acción:**
1. Verificar que el repo `second-brain-pack` en GitHub esté configurado como público
2. Asegurarse de que `Start.command` y `Start.bat` estén commiteados en main
3. Crear tag `v1.0.0`: `git tag v1.0.0 && git push origin v1.0.0`
4. Crear Release en GitHub con:
   - Título: "Second Brain Pack v1.0.0"
   - Body (en el release):
     ```
     Mac: doble-click en Start.command
     Windows: doble-click en Start.bat
     
     O cloná el repo: git clone https://github.com/FranciscoAnnoni/second-brain-pack
     ```
   - Assets: el zip del repo (GitHub lo genera automáticamente al crear el release)
5. Testear el one-liner de Mac de punta a punta en una sesión limpia

**Criterios de aceptación:**
- El repo es público en GitHub
- Existe el tag `v1.0.0` en el repo
- El Release v1.0.0 está creado y visible en la página de releases
- El one-liner de curl en README funciona desde una terminal sin el repo clonado

---

## Orden de ejecución

```
Wave 1 (paralelo):  1.1 + 1.2 + 1.3   ← bootstrap mac, windows, Start files
Wave 2 (secuencial): 2.1 → 2.2 → 2.3   ← GUI simplificada
Wave 3 (paralelo con 2): 3.1 + 3.2     ← brief.py fixes
Wave 4 (al final): 4.1 → 4.2           ← docs + release
```

## Tiempo estimado

| Wave | Tarea | Estimado |
|------|-------|---------|
| 1 | Bootstrap uv + Start files | 45 min |
| 2 | GUI simplificada + pantalla final + .app | 90 min |
| 3 | brief.py stdin + SOUL prefix | 20 min |
| 4 | README + Release | 30 min |
| **Total** | | **~3 horas** |
