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

Before installing, make sure you have:

- **Python 3.8 or later** — [python.org/downloads](https://www.python.org/downloads/)
- **Git** — [git-scm.com/downloads](https://git-scm.com/downloads)
- **Gemini CLI** (free) or **Claude Code** (paid) — the installer can set these up for you if you have npm

The installer handles everything else (vault setup, config, desktop shortcut).

---

## Install on Mac

Open Terminal and run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/FranciscoAnnoni/second-brain-pack/main/bootstrap/mac.sh)"
```

Or clone the repo first if you prefer:

```bash
git clone https://github.com/FranciscoAnnoni/second-brain-pack
cd second-brain-pack
bash bootstrap/mac.sh
```

The bootstrap script checks for Python, installs `customtkinter`, and opens the installer window.

**Step by step in the installer:**
1. Choose your AI agent (Gemini or Claude)
2. Choose whether to install it automatically (requires npm) or skip if already installed
3. Choose language and how much context to give the agent
4. Enter your name and the name of your assistant
5. Choose where to create the vault (default: `~/SecondBrain`)
6. Click Install

When done, a file called `Aria.app` (or whatever name you chose) appears on your Desktop. Double-click it to open a Terminal and run your brief.

**First run:**
```bash
brief
```

---

## Install on Windows

Open PowerShell and run:

```powershell
iwr -useb https://raw.githubusercontent.com/FranciscoAnnoni/second-brain-pack/main/bootstrap/windows.ps1 | iex
```

Or clone the repo first:

```powershell
git clone https://github.com/FranciscoAnnoni/second-brain-pack
cd second-brain-pack
powershell -ExecutionPolicy Bypass -File bootstrap\windows.ps1
```

The bootstrap script checks for Python, installs `customtkinter`, and opens the installer window.

**Step by step in the installer:** same as Mac above.

When done, a file called `Aria.bat` (or your chosen name) appears on your Desktop. Double-click it to open a terminal and run your brief.

**First run:**
```
brief
```

> **Note:** Windows may show a SmartScreen warning on the `.bat` file the first time. Click "More info" → "Run anyway". This happens because the file is new and unsigned — it is a plain text file, not an executable.

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
