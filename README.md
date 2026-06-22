# Second Brain Pack

A minimal, installable second brain powered by AI. Works with **Gemini CLI** (free) or **Claude Code**.

You get a personal vault of Markdown files, a daily brief that surfaces your open tasks, and an AI assistant that can answer questions about anything you've saved in your notes — study material, work docs, project notes, or any reference you load into the vault.

---

## What you get

- A local vault (plain Markdown files, no cloud lock-in, yours forever)
- An AI assistant configured with your name and style
- A `brief` command that shows your open tasks and last session summary
- An Obsidian-ready folder structure to organize notes, studies, and projects
- A desktop shortcut to launch your brief with a double-click
- Git history from day one

---

## How it works

```
vault/
├── SOUL.md          ← who your AI assistant is and how it behaves
├── MEMORY.md        ← long-term memory (key decisions, active projects)
├── pendientes.md    ← open tasks — source of truth for the brief
├── brief.py         ← generates your daily brief
├── config/
│   └── agent.yaml   ← which agent to use, language, context size
├── daily/           ← session logs (one file per day)
└── notes/
    ├── materias/    ← studies, courses, subjects
    ├── trabajo/     ← work and professional projects
    ├── proyectos/   ← personal projects
    ├── ideas/       ← brainstorming and loose thoughts
    └── recursos/    ← books, links, reference material
```

Everything the user knows goes inside `notes/`. The AI assistant reads those files when you ask questions — so if you load your study notes for a subject, you can ask questions about it and get answers grounded in your own material.

`SOUL.md` and `MEMORY.md` live outside `notes/` because they are agent configuration, not user knowledge.

---

## Requirements

- **Git** — [git-scm.com/downloads](https://git-scm.com/downloads)
- **Gemini CLI** (free) or **Claude Code** (paid) — the installer can set these up for you if you have npm

Python is installed automatically by the bootstrap script — no manual setup needed.

---

## Install on Mac

**Option 1 — double-click (easiest):**

1. Clone or download the repo
2. Double-click `Start.command`

> **macOS security warning:** the first time you open `Start.command`, macOS may block it. Right-click the file → "Open" → "Open" to allow it. This only happens once.

**Option 2 — one-liner from Terminal:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/FranciscoAnnoni/second-brain-pack/main/bootstrap/mac.sh)"
```

The bootstrap installs `uv` (Python manager) if needed, then opens the installer window.

**In the installer:**
1. Choose your AI agent and whether to install it automatically
2. Enter your assistant's name and your name
3. Choose where to create the vault (default: `~/SecondBrain`) and click Install

When done, `Aria.app` (or your chosen name) appears on your Desktop as a shortcut. Double-click it to run your brief.

**First run:**
```bash
brief
```

---

## Install on Windows

**Option 1 — double-click (easiest):**

1. Clone or download the repo
2. Double-click `Start.bat`

**Option 2 — one-liner from PowerShell:**

```powershell
iwr -useb https://raw.githubusercontent.com/FranciscoAnnoni/second-brain-pack/main/bootstrap/windows.ps1 | iex
```

The bootstrap installs `uv` (Python manager) if needed, then opens the installer window.

**In the installer:** same 3 steps as Mac above.

When done, `Aria.bat` (or your chosen name) appears on your Desktop. Double-click it to run your brief.

**First run:**
```
brief
```

> **Note:** Windows may show a SmartScreen warning on `Start.bat` or the desktop shortcut the first time. Click "More info" → "Run anyway". They are plain text files, not executables.

---

## Opening the vault in Obsidian

After installing, open Obsidian and add your vault folder as an existing vault:

1. Open Obsidian
2. Click "Open folder as vault"
3. Select the folder you chose during installation (default: `~/SecondBrain`)

All your notes in `notes/` will appear in the file explorer. You can create and edit them directly in Obsidian — the AI assistant reads whatever you put there.

---

## Using the brief

Run `brief` in any terminal. It reads `pendientes.md` and your latest daily log and asks your configured agent to generate a summary of what needs attention.

To add a task: edit `pendientes.md` directly, or tell the assistant to add it.
To mark something done: delete the line from `pendientes.md`.

---

## Customization

**Change the assistant's personality** — edit `SOUL.md` in your vault.

**Add your own note sections** — create subfolders inside `notes/`. The assistant will find files there automatically.

**Switch agents** — edit `config/agent.yaml` and change the `agent` field to `claude`, `gemini`, or `other`.

**Context size:**
- `compact` (~500 tokens) — best for Gemini free tier
- `standard` (~1500 tokens) — best for Claude Code

---

## AI agents

| Agent | Cost | How to install |
|-------|------|----------------|
| Gemini CLI | Free | `npm install -g @google/gemini-cli` |
| Claude Code | Paid (Max plan) | `npm install -g @anthropic-ai/claude-code` |

npm requires Node.js: [nodejs.org](https://nodejs.org)

---

## License

MIT
