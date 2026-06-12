#!/usr/bin/env python3
"""
brief.py — Daily brief for your Second Brain.

Usage:
    python brief.py           # uses configured agent
    python brief.py --dry-run # prints the prompt without calling the agent
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime


def find_vault_root():
    # brief.py lives at vault root, same level as config/
    candidate = Path(__file__).parent.resolve()
    if (candidate / "config" / "agent.yaml").exists():
        return candidate
    sys.exit("Error: config/agent.yaml not found. Did you run install.sh first?")


def parse_config(vault_root):
    """Parse config/agent.yaml without external dependencies."""
    path = vault_root / "config" / "agent.yaml"
    config = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            value = value.strip().strip('"').strip("'")
            # Skip inline comments
            if "#" in value:
                value = value[: value.index("#")].strip()
            config[key.strip()] = value
    return config


def read_pendientes(vault_root):
    path = vault_root / "pendientes.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def find_latest_daily(vault_root):
    daily_dir = vault_root / "daily"
    if not daily_dir.exists():
        return None, None
    files = [
        f
        for f in daily_dir.iterdir()
        if f.suffix == ".md"
        and not f.stem.startswith("reflection-")
        and f.stem != "daily"
    ]
    if not files:
        return None, None
    latest = max(files, key=lambda f: f.stem)
    return latest.stem, latest.read_text(encoding="utf-8")


def build_prompt(config, pendientes, daily_date, daily_content):
    today = datetime.now().strftime("%Y-%m-%d")
    lang = config.get("language", "es")

    if lang == "en":
        instructions = _build_prompt_en(pendientes, daily_date, daily_content, today)
    else:
        instructions = _build_prompt_es(pendientes, daily_date, daily_content, today)

    return instructions


def _build_prompt_es(pendientes, daily_date, daily_content, today):
    lines = [
        f"Hoy es {today}. Generá el brief del dia en base al estado actual del vault.",
        "",
        "## FORMATO (obligatorio, sin excepciones)",
        "",
        "**[ ULTIMA SESION ]**",
        "- que se hizo (del daily log, maximo 4-5 items concretos)",
        "",
        "**[ INMEDIATO ]**",
        "- items con urgencia real o deadline de hoy (omitir seccion si no hay ninguno)",
        "",
        "**[ CATEGORIA ]**",
        "- items de pendientes.md para esa categoria",
        "",
        "Reglas:",
        "- Titulos con **[ NOMBRE ]** en negrita y mayusculas",
        "- Un item por linea con -",
        "- Sin sub-bullets, sin tablas, sin ---, sin ##",
        "- Sin introduccion antes del primer bloque",
        "- Solo mostrar categorias con items activos",
        "- Items solo de pendientes.md — no inventar",
        "- Ultima linea: 'Algo que falta tachar o agregar?'",
        "",
    ]

    if daily_date and daily_content:
        lines += [
            f"## ULTIMA SESION (daily/{daily_date}.md)",
            daily_content.strip(),
            "",
        ]

    lines += [
        "## PENDIENTES ACTIVOS (pendientes.md)",
        pendientes.strip() if pendientes else "(sin pendientes registrados)",
    ]

    return "\n".join(lines)


def _build_prompt_en(pendientes, daily_date, daily_content, today):
    lines = [
        f"Today is {today}. Generate the daily brief based on the current vault state.",
        "",
        "## FORMAT (mandatory, no exceptions)",
        "",
        "**[ LAST SESSION ]**",
        "- what was done (from daily log, max 4-5 concrete items)",
        "",
        "**[ IMMEDIATE ]**",
        "- items with real urgency or deadline today (omit section if none)",
        "",
        "**[ CATEGORY ]**",
        "- items from pendientes.md for that category",
        "",
        "Rules:",
        "- Headers with **[ NAME ]** in bold and uppercase",
        "- One item per line with -",
        "- No sub-bullets, no tables, no ---, no ##",
        "- No intro before first block",
        "- Only show categories with active items",
        "- Items only from pendientes.md — do not invent",
        "- Last line: 'Anything missing or done?'",
        "",
    ]

    if daily_date and daily_content:
        lines += [
            f"## LAST SESSION (daily/{daily_date}.md)",
            daily_content.strip(),
            "",
        ]

    lines += [
        "## OPEN TASKS (pendientes.md)",
        pendientes.strip() if pendientes else "(no tasks registered)",
    ]

    return "\n".join(lines)


def call_agent(config, prompt):
    agent = config.get("agent", "gemini")

    if agent == "claude":
        binary, flag = "claude", "-p"
    elif agent == "gemini":
        binary, flag = "gemini", "-p"
    elif agent == "other":
        agent_cmd = config.get("agent_command", "")
        if not agent_cmd:
            sys.exit(
                "Error: agent is 'other' but agent_command is empty in config/agent.yaml"
            )
        parts = agent_cmd.split()
        binary, flag = parts[0], "-p"
    else:
        sys.exit(
            f"Error: unknown agent '{agent}'. Valid values: claude, gemini, other."
        )

    try:
        result = subprocess.run([binary, flag, prompt], text=True)
        sys.exit(result.returncode)
    except FileNotFoundError:
        sys.exit(
            f"Error: '{binary}' not found. Is {agent} CLI installed and in your PATH?"
        )


def main():
    dry_run = "--dry-run" in sys.argv

    vault_root = find_vault_root()
    config = parse_config(vault_root)
    pendientes = read_pendientes(vault_root)
    daily_date, daily_content = find_latest_daily(vault_root)
    prompt = build_prompt(config, pendientes, daily_date, daily_content)

    if dry_run:
        print(prompt)
        return

    call_agent(config, prompt)


if __name__ == "__main__":
    main()
