#!/usr/bin/env python3
"""
Second Brain Pack — GUI Installer

Mac:     bash bootstrap/mac.sh
Windows: powershell -ExecutionPolicy Bypass -File bootstrap/windows.ps1
"""

import sys
import subprocess
import customtkinter as ctk

import os
import re
import platform
import shutil
import threading
from datetime import date
from pathlib import Path

from tkinter import filedialog, messagebox

# ── Constants ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent.resolve()
TEMPLATE_DIR = SCRIPT_DIR / "template"
IS_MAC = platform.system() == "Darwin"
IS_WIN = platform.system() == "Windows"

GEMINI_PKG = "@google/gemini-cli"
CLAUDE_PKG = "@anthropic-ai/claude-code"

W, H = 520, 640


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
        self.agent_name = ctk.StringVar(value="Aria")
        self.user_name = ctk.StringVar(value="")
        self.vault_path = ctk.StringVar(value=str(Path.home() / "SecondBrain"))
        self.other_agent_cmd = ctk.StringVar(value="")

        self._install_error = None
        self._other_cmd_entry = None

        self.show_screen_config()

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

    # ── Screen 1: Config ───────────────────────────────────────────────────
    def show_screen_config(self):
        self._clear()
        scroll = ctk.CTkScrollableFrame(self, width=W - 40, height=H - 40)
        scroll.pack(fill="both", expand=True, padx=16, pady=16)

        self._header(
            scroll,
            "Second Brain",
            "Configura tu asistente de IA en menos de 10 minutos.",
        )

        # -- Agente
        self._section(scroll, "Agente")

        ctk.CTkRadioButton(
            scroll,
            text="Gemini CLI   (gratuito, recomendado)",
            variable=self.agent,
            value="gemini",
            command=self._on_agent_change,
        ).pack(anchor="w", padx=36, pady=3)

        ctk.CTkRadioButton(
            scroll,
            text="Claude Code   (requiere suscripcion)",
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

        ctk.CTkCheckBox(
            scroll,
            text="Instalar el agente automaticamente  (requiere npm)",
            variable=self.install_agent,
        ).pack(anchor="w", padx=36, pady=(6, 3))

        self._divider(scroll)

        # -- Identidad del asistente
        self._section(scroll, "Como se llama tu asistente?")
        ctk.CTkEntry(
            scroll, textvariable=self.agent_name, width=360, placeholder_text="Aria"
        ).pack(anchor="w", padx=20, pady=(2, 6))

        self._section(scroll, "Como te llamas vos?")
        ctk.CTkEntry(
            scroll,
            textvariable=self.user_name,
            width=360,
            placeholder_text="Tu nombre",
        ).pack(anchor="w", padx=20, pady=(2, 6))

        self._divider(scroll)

        # -- Vault
        self._section(scroll, "Carpeta del vault")
        vault_row = ctk.CTkFrame(scroll, fg_color="transparent")
        vault_row.pack(anchor="w", padx=20, pady=4, fill="x")
        ctk.CTkEntry(vault_row, textvariable=self.vault_path, width=300).pack(
            side="left", padx=(0, 8)
        )
        ctk.CTkButton(
            vault_row, text="...", width=44, command=self._browse_vault
        ).pack(side="left")

        ctk.CTkButton(
            scroll, text="Instalar  →", width=200, command=self._validate_and_install
        ).pack(pady=24)

    def _on_agent_change(self):
        if self.agent.get() == "other":
            self._other_cmd_entry.pack(anchor="w", padx=52, pady=(0, 6))
        else:
            self._other_cmd_entry.pack_forget()

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
            messagebox.showerror("Falta un dato", "Ingresa el comando del agente.")
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

    # ── Screen 2: Installing ───────────────────────────────────────────────
    def show_screen_installing(self):
        self._clear()

        ctk.CTkLabel(
            self, text="Instalando...", font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(44, 16))

        self._progress_bar = ctk.CTkProgressBar(self, width=440)
        self._progress_bar.set(0)
        self._progress_bar.pack(pady=4)

        self._progress_label = ctk.CTkLabel(
            self, text="Iniciando...", font=ctk.CTkFont(size=12), text_color="gray"
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
        lang = "es"
        ctx = "standard" if agent == "claude" else "compact"

        # 1. Install agent CLI
        if self.install_agent.get() and agent != "other":
            pkg = GEMINI_PKG if agent == "gemini" else CLAUDE_PKG
            self._log(8, f"Instalando {pkg} via npm...")
            if not shutil.which("npm"):
                raise RuntimeError(
                    "npm no encontrado. Instala Node.js desde https://nodejs.org "
                    "y volvé a intentarlo."
                )
            result = subprocess.run(
                ["npm", "install", "-g", pkg], capture_output=True, text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"Error al instalar {pkg}:\n{result.stderr[:600]}")
            self._log(20, f"✓ {agent} CLI instalado")

        # 2. Copy template
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

        # 3. Apply SOUL/MEMORY variant
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

        # 4. Write config/agent.yaml
        agent_cmd = self.other_agent_cmd.get().strip() if agent == "other" else ""
        config_yaml = (
            f"# Second Brain — Agent Configuration\n"
            f"# Generated by install.py on {date.today()}\n\n"
            f"agent: {agent}\n"
            f'agent_command: "{agent_cmd}"\n'
            f"language: {lang}\n"
            f'agent_name: "{agent_name}"\n'
            f'user_name: "{user_name}"\n'
            f'vault_path: "{vault}"\n'
            f"context_size: {ctx}\n"
        )
        (vault / "config" / "agent.yaml").write_text(config_yaml, encoding="utf-8")
        self._log(60, "✓ config/agent.yaml escrito")

        # 5. Add `brief` alias to shell
        self._log(73, "Configurando alias 'brief'...")
        self._add_brief_alias(vault)
        self._log(79, "✓ Alias 'brief' configurado")

        # 6. Create desktop app / shortcut
        self._log(83, "Creando acceso directo...")
        if IS_MAC:
            self._create_mac_app(vault, agent_name)
        elif IS_WIN:
            self._create_windows_shortcut(vault, agent_name)
        self._log(90, f"✓ Acceso directo: {agent_name}")

        # 7. Git init
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
    def _add_brief_alias(self, vault):
        alias = f"alias brief='cd \"{vault}\" && uv run brief.py'"

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
            ps_fn = f'function brief {{ Set-Location "{vault}"; uv run brief.py }}'
            text = profile.read_text(encoding="utf-8") if profile.exists() else ""
            if "function brief" not in text:
                with profile.open("a", encoding="utf-8") as fh:
                    fh.write(f"\n# Second Brain\n{ps_fn}\n")

    def _create_mac_app(self, vault, agent_name):
        app_id = agent_name.replace(" ", "")
        apps_dir = Path.home() / "Applications"
        apps_dir.mkdir(exist_ok=True)
        app = apps_dir / f"{app_id}.app"
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
osascript -e 'tell application "Terminal" to do script "cd \\"{vault}\\" && uv run brief.py"'
osascript -e 'tell application "Terminal" to activate'
""",
            encoding="utf-8",
        )
        exec_file.chmod(0o755)

        # Symlink on Desktop pointing to ~/Applications
        desktop = Path.home() / "Desktop"
        link = desktop / f"{app_id}.app"
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(app)

    def _create_windows_shortcut(self, vault, agent_name):
        desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
        bat = desktop / f"{agent_name}.bat"
        bat.write_text(
            f"@echo off\r\ntitle {agent_name} — Second Brain\r\n"
            f'cd /d "{vault}"\r\n'
            "uv run brief.py\r\n"
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
            self, text="← Volver al inicio", command=self.show_screen_config
        ).pack(pady=16)

    # ── Screen 3: Done ─────────────────────────────────────────────────────
    def show_screen_done(self):
        self._clear()
        vault = Path(self.vault_path.get())
        agent = self.agent.get()
        agent_name = self.agent_name.get().strip() or "Aria"
        agent_binary = {"gemini": "gemini", "claude": "claude"}.get(
            agent, self.other_agent_cmd.get().strip()
        )

        ctk.CTkLabel(
            self,
            text="Listo!",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#4CAF50",
        ).pack(pady=(32, 4))
        ctk.CTkLabel(
            self,
            text="Tu segundo cerebro esta configurado.",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        ).pack(pady=(0, 10))

        # Vault info card
        card = ctk.CTkFrame(self, width=460)
        card.pack(padx=20, pady=4, fill="x")
        ctk.CTkLabel(
            card,
            text=f"Vault:  {vault}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(pady=(10, 8), padx=16, anchor="w")

        # Steps
        steps = ctk.CTkFrame(self, width=460)
        steps.pack(padx=20, pady=8, fill="x")

        ctk.CTkLabel(
            steps, text="Proximos pasos", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(12, 6), padx=16, anchor="w")

        # Step 1: Login
        ctk.CTkLabel(
            steps,
            text=f"1.  Activa tu agente  (solo la primera vez)",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(4, 0))
        ctk.CTkLabel(
            steps,
            text=f"Abre una nueva terminal y ejecuta:  {agent_binary}",
            font=ctk.CTkFont(size=12),
        ).pack(anchor="w", padx=16, pady=(2, 0))
        ctk.CTkLabel(
            steps,
            text="Se abrira el browser para iniciar sesion. Solo se hace una vez.",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        ).pack(anchor="w", padx=16, pady=(0, 4))
        ctk.CTkButton(
            steps,
            text="Abrir Terminal",
            width=140,
            command=lambda: self._open_terminal_with_agent(agent_binary),
        ).pack(anchor="w", padx=16, pady=(2, 10))

        ctk.CTkFrame(steps, height=1, fg_color="#333").pack(fill="x", padx=16, pady=4)

        # Step 2: Obsidian
        ctk.CTkLabel(
            steps,
            text="2.  Agrega el vault en Obsidian",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(8, 0))
        ctk.CTkLabel(
            steps,
            text="File → Open folder as vault → selecciona esta carpeta:",
            font=ctk.CTkFont(size=12),
        ).pack(anchor="w", padx=16, pady=(2, 0))
        ctk.CTkLabel(
            steps, text=str(vault), font=ctk.CTkFont(size=11), text_color="#64B5F6"
        ).pack(anchor="w", padx=16, pady=(2, 4))
        ctk.CTkButton(
            steps, text="Abrir Obsidian", width=140, command=self._open_obsidian
        ).pack(anchor="w", padx=16, pady=(2, 12))

        # Bottom buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=12)
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

    def _open_terminal_with_agent(self, agent_binary):
        if IS_MAC:
            subprocess.Popen([
                "osascript",
                "-e", f'tell application "Terminal" to do script "{agent_binary}"',
                "-e", 'tell application "Terminal" to activate',
            ])
        elif IS_WIN:
            subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", agent_binary])

    def _open_obsidian(self):
        if IS_MAC:
            result = subprocess.run(["open", "-a", "Obsidian"], capture_output=True)
            if result.returncode != 0:
                messagebox.showinfo(
                    "Obsidian", "Obsidian no encontrado.\nDescargalo en https://obsidian.md"
                )
        elif IS_WIN:
            try:
                subprocess.Popen(["obsidian"])
            except FileNotFoundError:
                messagebox.showinfo(
                    "Obsidian", "Obsidian no encontrado.\nDescargalo en https://obsidian.md"
                )


# ── Entry point ────────────────────────────────────────────────────────────
def main():
    if not TEMPLATE_DIR.exists():
        print(f"Error: no se encontro template/ en {TEMPLATE_DIR}")
        print("Corre install.py desde la raiz del repo second-brain-pack.")
        sys.exit(1)
    app = InstallerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
