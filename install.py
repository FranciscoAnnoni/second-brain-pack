#!/usr/bin/env python3
"""
Second Brain Pack — GUI Installer
Python 3.8+ required. customtkinter auto-installed on first run.

Mac:     bash bootstrap/mac.sh
Windows: powershell -ExecutionPolicy Bypass -File bootstrap/windows.ps1
"""

import sys
import subprocess

# Auto-install customtkinter before importing anything else
try:
    import customtkinter as ctk
except ImportError:
    print("Instalando customtkinter (solo la primera vez)...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "customtkinter", "--quiet"]
    )
    import customtkinter as ctk

import os
import re
import platform
import shutil
import threading
import webbrowser
from datetime import date
from pathlib import Path

try:
    from tkinter import filedialog, messagebox
except ImportError:
    print("Error: tkinter no disponible.")
    print("En Mac: instala Python desde python.org (no via brew).")
    print("En Windows: reinstala Python marcando 'tcl/tk and IDLE'.")
    sys.exit(1)

# ── Constants ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
TEMPLATE_DIR = SCRIPT_DIR / "template"
IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"

GEMINI_PKG = "@google/gemini-cli"
CLAUDE_PKG = "@anthropic-ai/claude-code"
MCP_PKG = "@modelcontextprotocol/server-sequential-thinking"
OBSIDIAN_URL = "https://obsidian.md/download"

W, H = 520, 620


# ── Main App ───────────────────────────────────────────────────────────────
class InstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Second Brain — Instalador")
        self.geometry(f"{W}x{H}")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # User choices
        self.agent = ctk.StringVar(value="gemini")
        self.install_agent = ctk.BooleanVar(value=False)
        self.has_obsidian = ctk.BooleanVar(value=False)
        self.open_obsidian_dl = ctk.BooleanVar(value=False)
        self.install_mcp = ctk.BooleanVar(value=True)
        self.agent_name = ctk.StringVar(value="Aria")
        self.user_name = ctk.StringVar(value="")
        self.language = ctk.StringVar(value="es")
        self.context_size = ctk.StringVar(value="compact")
        self.vault_path = ctk.StringVar(value=str(Path.home() / "SecondBrain"))
        self.other_agent_cmd = ctk.StringVar(value="")

        self._install_error = None
        self._other_cmd_entry = None

        self.show_screen_agent()

    # ── Helpers ────────────────────────────────────────────────────────────
    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _header(self, parent, title, subtitle=None):
        ctk.CTkLabel(
            parent, text=title, font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(24, 4))
        if subtitle:
            ctk.CTkLabel(
                parent, text=subtitle, font=ctk.CTkFont(size=13), text_color="gray"
            ).pack(pady=(0, 12))

    def _divider(self, parent):
        ctk.CTkFrame(parent, height=1, fg_color="#333").pack(
            fill="x", padx=20, pady=10
        )

    def _section(self, parent, text):
        ctk.CTkLabel(
            parent, text=text, font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=20, pady=(4, 2))

    # ── Screen 1: Agent ────────────────────────────────────────────────────
    def show_screen_agent(self):
        self._clear()
        scroll = ctk.CTkScrollableFrame(self, width=W - 40, height=H - 40)
        scroll.pack(fill="both", expand=True, padx=16, pady=16)

        self._header(
            scroll,
            "Second Brain",
            "Configura tu asistente de IA en menos de 10 minutos.",
        )

        self._section(scroll, "Que agente de IA queres usar?")

        ctk.CTkRadioButton(
            scroll,
            text="Gemini CLI   (gratuito, recomendado para empezar)",
            variable=self.agent,
            value="gemini",
            command=self._on_agent_change,
        ).pack(anchor="w", padx=36, pady=3)

        ctk.CTkRadioButton(
            scroll,
            text="Claude Code   (mas potente, requiere suscripcion)",
            variable=self.agent,
            value="claude",
            command=self._on_agent_change,
        ).pack(anchor="w", padx=36, pady=3)

        ctk.CTkRadioButton(
            scroll,
            text="Otro...",
            variable=self.agent,
            value="other",
            command=self._on_agent_change,
        ).pack(anchor="w", padx=36, pady=3)

        self._other_cmd_entry = ctk.CTkEntry(
            scroll,
            textvariable=self.other_agent_cmd,
            placeholder_text="Comando del agente  (ej: llm)",
            width=300,
        )
        # shown/hidden by _on_agent_change

        self._divider(scroll)
        self._section(scroll, "Instalacion del agente")

        ctk.CTkCheckBox(
            scroll,
            text="Instalar el agente por mi  (requiere npm en el sistema)",
            variable=self.install_agent,
        ).pack(anchor="w", padx=36, pady=3)

        self._divider(scroll)
        self._section(scroll, "Obsidian  (visor de notas, opcional)")

        ctk.CTkCheckBox(
            scroll,
            text="Ya tengo Obsidian instalado",
            variable=self.has_obsidian,
        ).pack(anchor="w", padx=36, pady=3)

        ctk.CTkCheckBox(
            scroll,
            text="Abrir pagina de descarga de Obsidian",
            variable=self.open_obsidian_dl,
        ).pack(anchor="w", padx=36, pady=3)

        self._divider(scroll)
        self._section(scroll, "MCP Sequential Thinking  (mejora el razonamiento)")

        ctk.CTkCheckBox(
            scroll,
            text="Instalar MCP sequential-thinking  (requiere npm)",
            variable=self.install_mcp,
        ).pack(anchor="w", padx=36, pady=3)

        ctk.CTkButton(
            scroll,
            text="Siguiente  →",
            width=200,
            command=self.show_screen_config,
        ).pack(pady=24)

    def _on_agent_change(self):
        if self.agent.get() == "other":
            self._other_cmd_entry.pack(anchor="w", padx=52, pady=(0, 6))
        else:
            self._other_cmd_entry.pack_forget()
        # Suggest context size
        self.context_size.set("standard" if self.agent.get() == "claude" else "compact")

    # ── Screen 2: Config ───────────────────────────────────────────────────
    def show_screen_config(self):
        self._clear()
        scroll = ctk.CTkScrollableFrame(self, width=W - 40, height=H - 40)
        scroll.pack(fill="both", expand=True, padx=16, pady=16)

        self._header(scroll, "Configuracion")

        self._section(scroll, "Como se llama tu asistente?")
        ctk.CTkEntry(
            scroll, textvariable=self.agent_name, width=360, placeholder_text="Aria"
        ).pack(anchor="w", padx=20, pady=(2, 10))

        self._section(scroll, "Como te llamas vos?")
        ctk.CTkEntry(
            scroll,
            textvariable=self.user_name,
            width=360,
            placeholder_text="Tu nombre",
        ).pack(anchor="w", padx=20, pady=(2, 10))

        self._divider(scroll)
        self._section(scroll, "Idioma del brief")
        lang_row = ctk.CTkFrame(scroll, fg_color="transparent")
        lang_row.pack(anchor="w", padx=20, pady=4)
        ctk.CTkRadioButton(
            lang_row, text="Espanol", variable=self.language, value="es"
        ).pack(side="left", padx=(0, 24))
        ctk.CTkRadioButton(
            lang_row, text="English", variable=self.language, value="en"
        ).pack(side="left")

        self._divider(scroll)
        self._section(scroll, "Cuanto contexto le das al agente?")
        ctk.CTkRadioButton(
            scroll,
            text="Compact   — ~500 tokens  (Gemini free, recomendado)",
            variable=self.context_size,
            value="compact",
        ).pack(anchor="w", padx=36, pady=3)
        ctk.CTkRadioButton(
            scroll,
            text="Standard  — ~1500 tokens  (Claude Code)",
            variable=self.context_size,
            value="standard",
        ).pack(anchor="w", padx=36, pady=3)

        self._divider(scroll)
        self._section(scroll, "Carpeta donde instalar el vault")
        vault_row = ctk.CTkFrame(scroll, fg_color="transparent")
        vault_row.pack(anchor="w", padx=20, pady=4, fill="x")
        ctk.CTkEntry(vault_row, textvariable=self.vault_path, width=300).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkButton(
            vault_row, text="...", width=44, command=self._browse_vault
        ).pack(side="left")

        nav = ctk.CTkFrame(scroll, fg_color="transparent")
        nav.pack(fill="x", pady=24)
        ctk.CTkButton(
            nav,
            text="← Atras",
            width=120,
            fg_color="gray30",
            command=self.show_screen_agent,
        ).pack(side="left", padx=20)
        ctk.CTkButton(
            nav,
            text="Instalar  →",
            width=160,
            command=self._validate_and_install,
        ).pack(side="right", padx=20)

    def _browse_vault(self):
        path = filedialog.askdirectory(
            title="Elegir carpeta para el vault", initialdir=str(Path.home())
        )
        if path:
            self.vault_path.set(path)

    def _validate_and_install(self):
        if not self.user_name.get().strip():
            messagebox.showerror("Falta un dato", "Ingresa tu nombre.")
            return
        if self.agent.get() == "other" and not self.other_agent_cmd.get().strip():
            messagebox.showerror(
                "Falta un dato", "Ingresa el comando del agente."
            )
            return
        vault = Path(self.vault_path.get())
        if vault.exists() and any(vault.iterdir()):
            ok = messagebox.askyesno(
                "Carpeta existente",
                f"{vault} ya tiene contenido.\n\nInstalar encima?",
            )
            if not ok:
                return
        self.show_screen_installing()

    # ── Screen 3: Installing ───────────────────────────────────────────────
    def show_screen_installing(self):
        self._clear()

        ctk.CTkLabel(
            self, text="Instalando...", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(44, 16))

        self._progress_bar = ctk.CTkProgressBar(self, width=440)
        self._progress_bar.set(0)
        self._progress_bar.pack(pady=4)

        self._progress_label = ctk.CTkLabel(
            self,
            text="Iniciando...",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self._progress_label.pack(pady=6)

        self._log_box = ctk.CTkTextbox(
            self,
            width=460,
            height=320,
            state="disabled",
            font=ctk.CTkFont(family="Courier" if IS_MAC else "Consolas", size=11),
        )
        self._log_box.pack(padx=20, pady=8)

        threading.Thread(target=self._run_installation, daemon=True).start()

    def _log(self, pct, message):
        def _do():
            self._progress_bar.set(pct / 100)
            self._progress_label.configure(text=message)
            self._log_box.configure(state="normal")
            self._log_box.insert("end", f"{message}\n")
            self._log_box.see("end")
            self._log_box.configure(state="disabled")

        self.after(0, _do)

    def _run_installation(self):
        try:
            self._do_install()
            self.after(0, self.show_screen_done)
        except Exception as exc:
            self._install_error = str(exc)
            self.after(0, self._show_error)

    def _do_install(self):
        vault = Path(self.vault_path.get())
        agent = self.agent.get()
        agent_name = self.agent_name.get().strip() or "Aria"
        user_name = self.user_name.get().strip()
        lang = self.language.get()
        ctx = self.context_size.get()
        python_bin = sys.executable

        # 1. Open Obsidian download page
        if self.open_obsidian_dl.get():
            self._log(3, "Abriendo pagina de descarga de Obsidian...")
            webbrowser.open(OBSIDIAN_URL)

        # 2. Install agent CLI
        if self.install_agent.get() and agent != "other":
            pkg = GEMINI_PKG if agent == "gemini" else CLAUDE_PKG
            self._log(8, f"Instalando {pkg} via npm...")
            if not shutil.which("npm"):
                raise RuntimeError(
                    "npm no encontrado. Instala Node.js desde https://nodejs.org "
                    "y volvé a intentarlo."
                )
            result = subprocess.run(
                ["npm", "install", "-g", pkg],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"Error al instalar {pkg}:\n{result.stderr[:600]}"
                )
            self._log(20, f"✓ {agent} CLI instalado")

        # 3. Copy template
        self._log(25, "Copiando archivos del vault...")
        vault.mkdir(parents=True, exist_ok=True)
        for item in TEMPLATE_DIR.iterdir():
            dest = vault / item.name
            if item.is_dir():
                shutil.copytree(str(item), str(dest), dirs_exist_ok=True)
            else:
                shutil.copy2(str(item), str(dest))
        (vault / "config" / "agent.yaml.example").unlink(missing_ok=True)
        self._log(38, "✓ Archivos copiados")

        # 4. Apply SOUL/MEMORY variant
        self._log(42, "Configurando SOUL.md y MEMORY.md...")
        variants = vault / "variants"
        shutil.copy2(str(variants / f"soul-{ctx}.md"), str(vault / "SOUL.md"))
        shutil.copy2(str(variants / f"memory-{ctx}.md"), str(vault / "MEMORY.md"))
        shutil.rmtree(str(variants), ignore_errors=True)

        soul = (vault / "SOUL.md").read_text(encoding="utf-8")
        soul = soul.replace("{{AGENT_NAME}}", agent_name)
        soul = soul.replace("{{USER_NAME}}", user_name)
        soul = soul.replace("{{LANGUAGE}}", lang)
        (vault / "SOUL.md").write_text(soul, encoding="utf-8")
        self._log(52, f"✓ SOUL.md personalizado para {agent_name}")

        # 5. Write config/agent.yaml
        agent_cmd = self.other_agent_cmd.get().strip() if agent == "other" else ""
        has_obs = str(self.has_obsidian.get()).lower()
        config_yaml = (
            f"# Second Brain — Agent Configuration\n"
            f"# Generated by install.py on {date.today()}\n\n"
            f"agent: {agent}\n"
            f'agent_command: "{agent_cmd}"\n'
            f"language: {lang}\n"
            f'agent_name: "{agent_name}"\n'
            f'user_name: "{user_name}"\n'
            f'vault_path: "{vault}"\n'
            f"obsidian: {has_obs}\n"
            f"context_size: {ctx}\n"
        )
        (vault / "config" / "agent.yaml").write_text(config_yaml, encoding="utf-8")
        self._log(58, "✓ config/agent.yaml escrito")

        # 6. Install MCP sequential-thinking (optional)
        if self.install_mcp.get():
            if not shutil.which("npm"):
                self._log(62, "! npm no encontrado — MCP omitido")
            else:
                self._log(62, "Instalando MCP sequential-thinking...")
                mcp_dir = vault / ".mcp" / "sequential-thinking"
                mcp_dir.mkdir(parents=True, exist_ok=True)
                subprocess.run(
                    ["npm", "install", MCP_PKG, "--silent"],
                    cwd=str(mcp_dir),
                    capture_output=True,
                )
                if agent == "claude":
                    self._configure_claude_mcp(vault, mcp_dir)
                self._log(70, "✓ MCP sequential-thinking instalado")

        # 7. Add `brief` alias to shell
        self._log(73, "Configurando alias 'brief'...")
        self._add_brief_alias(vault, python_bin)
        self._log(79, "✓ Alias 'brief' configurado")

        # 8. Create desktop app / shortcut
        self._log(83, "Creando acceso directo en el escritorio...")
        if IS_MAC:
            self._create_mac_app(vault, agent_name, python_bin)
        elif IS_WIN:
            self._create_windows_shortcut(vault, agent_name, python_bin)
        self._log(90, f"✓ Acceso directo: {agent_name}")

        # 9. Git init
        self._log(93, "Inicializando repositorio git...")
        subprocess.run(["git", "init", "--quiet"], cwd=str(vault), capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=str(vault), capture_output=True)
        subprocess.run(
            ["git", "commit", "--quiet", "-m", "Initial commit — Second Brain instalado"],
            cwd=str(vault),
            capture_output=True,
        )
        self._log(100, "✓ Instalacion completa")

    # ── Install helpers ────────────────────────────────────────────────────
    def _configure_claude_mcp(self, vault, mcp_dir):
        import json

        settings_path = vault / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        cfg = {}
        if settings_path.exists():
            try:
                cfg = json.loads(settings_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        mcp_bin = mcp_dir / "node_modules" / ".bin" / "mcp-server-sequential-thinking"
        cfg.setdefault("mcpServers", {})["sequential-thinking"] = {
            "command": "node",
            "args": [str(mcp_bin)],
        }
        settings_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    def _add_brief_alias(self, vault, python_bin):
        alias = f"alias brief='cd \"{vault}\" && \"{python_bin}\" brief.py'"

        if IS_MAC:
            shell = os.environ.get("SHELL", "")
            rc = Path.home() / (".zshrc" if "zsh" in shell else ".bash_profile")
            text = rc.read_text(encoding="utf-8") if rc.exists() else ""
            if "alias brief=" in text:
                text = re.sub(r"alias brief=.*", alias, text)
                rc.write_text(text, encoding="utf-8")
            else:
                with rc.open("a", encoding="utf-8") as fh:
                    fh.write(f"\n# Second Brain\n{alias}\n")

        elif IS_WIN:
            profile_dir = (
                Path(os.environ.get("USERPROFILE", str(Path.home())))
                / "Documents"
                / "WindowsPowerShell"
            )
            profile_dir.mkdir(parents=True, exist_ok=True)
            profile = profile_dir / "Microsoft.PowerShell_profile.ps1"
            ps_fn = (
                f'function brief {{ Set-Location "{vault}"; '
                f'& "{python_bin}" brief.py }}'
            )
            text = profile.read_text(encoding="utf-8") if profile.exists() else ""
            if "function brief" not in text:
                with profile.open("a", encoding="utf-8") as fh:
                    fh.write(f"\n# Second Brain\n{ps_fn}\n")

    def _create_mac_app(self, vault, agent_name, python_bin):
        app_id = agent_name.replace(" ", "")
        desktop = Path.home() / "Desktop"
        app = desktop / f"{app_id}.app"
        macos = app / "Contents" / "MacOS"
        macos.mkdir(parents=True, exist_ok=True)

        (app / "Contents" / "Info.plist").write_text(
            f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleExecutable</key><string>{app_id}</string>
  <key>CFBundleIdentifier</key><string>com.secondbrain.{app_id.lower()}</string>
  <key>CFBundleName</key><string>{agent_name}</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>CFBundlePackageType</key><string>APPL</string>
</dict></plist>
""",
            encoding="utf-8",
        )

        exec_file = macos / app_id
        exec_file.write_text(
            f"""#!/bin/bash
osascript -e 'tell application "Terminal" to do script "cd \\"{vault}\\" && \\"{python_bin}\\" brief.py"'
osascript -e 'tell application "Terminal" to activate'
""",
            encoding="utf-8",
        )
        exec_file.chmod(0o755)

    def _create_windows_shortcut(self, vault, agent_name, python_bin):
        desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
        bat = desktop / f"{agent_name}.bat"
        bat.write_text(
            f"@echo off\r\ntitle {agent_name} — Second Brain\r\n"
            f'cd /d "{vault}"\r\n'
            f'"{python_bin}" brief.py\r\n'
            "pause\r\n",
            encoding="utf-8",
        )

    # ── Error screen ───────────────────────────────────────────────────────
    def _show_error(self):
        self._clear()
        ctk.CTkLabel(
            self,
            text="Algo salio mal",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f44336",
        ).pack(pady=(44, 16))

        box = ctk.CTkTextbox(self, width=460, height=240)
        box.insert("1.0", self._install_error or "Error desconocido")
        box.configure(state="disabled")
        box.pack(padx=20, pady=8)

        ctk.CTkLabel(
            self, text="Corrige el error y volvé a intentar.", text_color="gray"
        ).pack(pady=8)
        ctk.CTkButton(
            self, text="← Volver al inicio", command=self.show_screen_agent
        ).pack(pady=16)

    # ── Screen 4: Done ─────────────────────────────────────────────────────
    def show_screen_done(self):
        self._clear()
        vault = Path(self.vault_path.get())
        agent_name = self.agent_name.get().strip() or "Aria"
        app_id = agent_name.replace(" ", "")

        ctk.CTkLabel(
            self,
            text="Listo!",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#4CAF50",
        ).pack(pady=(48, 8))
        ctk.CTkLabel(
            self,
            text="Tu segundo cerebro esta configurado.",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        ).pack(pady=(0, 20))

        card = ctk.CTkFrame(self, width=460)
        card.pack(padx=20, pady=8, fill="x")

        ctk.CTkLabel(
            card,
            text=f"Vault:  {vault}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(pady=(12, 4), padx=16, anchor="w")

        ctk.CTkFrame(card, height=1, fg_color="#333").pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(
            card,
            text="Como usar el brief:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(pady=(6, 4), padx=16, anchor="w")

        if IS_MAC:
            line1 = "Abri una nueva terminal  →  escribi:  brief"
            line2 = f"O doble-click en:  {app_id}.app  (en tu escritorio)"
        else:
            line1 = "Abri PowerShell o cmd  →  escribi:  brief"
            line2 = f"O doble-click en:  {app_id}.bat  (en tu escritorio)"

        ctk.CTkLabel(card, text=line1, font=ctk.CTkFont(size=12)).pack(
            pady=2, padx=16, anchor="w"
        )
        ctk.CTkLabel(card, text=line2, font=ctk.CTkFont(size=12)).pack(
            pady=(2, 14), padx=16, anchor="w"
        )

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=24)
        ctk.CTkButton(
            btn_row,
            text="Abrir vault",
            width=160,
            command=lambda: (
                subprocess.run(["open", str(vault)])
                if IS_MAC
                else subprocess.run(["explorer", str(vault)])
            ),
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            btn_row,
            text="Cerrar",
            width=100,
            fg_color="gray30",
            command=self.destroy,
        ).pack(side="left", padx=8)


# ── Entry point ────────────────────────────────────────────────────────────
def main():
    if not TEMPLATE_DIR.exists():
        print(f"Error: no se encontro template/ en {TEMPLATE_DIR}")
        print("Corré install.py desde la raiz del repo second-brain-pack.")
        sys.exit(1)
    app = InstallerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
