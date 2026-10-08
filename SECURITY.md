# Security

## What Adams touches on your machine
- `adams install` creates symlinks (`~/.claude/skills/adams`, `~/.copilot/skills/adams`, `~/.local/bin/adams`) and adds two hooks to `~/.claude/settings.json`, after saving a backup as `settings.json.adams-backup`. Preview it with `adams install --dry-run`; undo it with `adams uninstall`.
- The hooks run local scripts only. The git guardrail reads the command the agent is about to run and blocks a short list of risky git commands. Nothing is sent anywhere.
- On first use the layout checkers install pinned dependencies (Playwright and Chromium, `pdfplumber`, `pillow`). Set `ADAMS_AUTO_INSTALL=0` to forbid that; Adams then prints the exact command instead.
- `web_balance.js` reads pages you point it at. It signs in only with credentials you put in environment variables (`LB_EMAIL`, `LB_PASSWORD`) for test accounts, and stores sessions in a folder you choose. Never use real customer accounts, and never commit session files.
- There is no telemetry. Adams hooks and scripts make no network calls except the daily release check (`scripts/update.py`) and dependency installs on first run of the line-balance scripts, and they read only the working folder.

## Reporting a vulnerability
Please do not open a public issue. Use GitHub's private vulnerability reporting on this repository (Security tab, "Report a vulnerability"). Include the version, what you saw and how to reproduce it. You will get an answer within a week.

## Supported versions
Only the latest release on `main`.
