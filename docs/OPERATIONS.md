# Adams operations

Moved out of `SKILL.md` to keep the always-loaded router small.

## Install and use on any machine (Claude Code and Copilot CLI, Warp or any terminal)

- `adams install` links the skill for Claude Code (`~/.claude/skills/adams`) and Copilot CLI (`~/.copilot/skills/adams`), puts `adams` on the PATH (`~/.local/bin`) and registers the two hooks. `adams doctor` reports what is missing and how to fix it; `adams uninstall` removes exactly what install added; `adams sync` writes the Copilot instructions (`ALWAYS.md`, plus an optional personal overlay).
- Claude Code reads `ALWAYS.md` through an `@` import in `~/.claude/CLAUDE.md` (add `@<folder printed by adams where>/ALWAYS.md`). Copilot has no prompt hook, so its instructions file does that job.
- Scripts are plain Python and Node and resolve their own folder, so they run the same from either tool and from CI.
- Where a module says "spawn a reviewer agent", Copilot uses its own subagent if one is available; otherwise do the fresh-eyes pass in a separate step and say so.

## Profiles: team default and personal rules

`hzlint.py` and `check.py` read an active profile (rule groups on or off). Order: `ADAMS_PROFILE`, then the nearest `.adams/config.json` upward from the working folder (`{"profile": "strict-ar"}`), then `~/.config/adams/config.json`, then the plugin option `profile` (reaches hooks as `CLAUDE_PLUGIN_OPTION_PROFILE`), then `default`. Profiles are `<name>.json` files in `~/.config/adams/profiles/` or `config/profiles/` and may `extends` another. Shipped: `default` (universal AI-writing tells only) and `strict-ar` (Arabic style, register and post layout). Personal rules, such as religious-word or dash bans, live in a personal profile and `~/.config/adams/personal.md`, never in this repo.

## Maintenance: one repo, one source

- The only source is the Adams repo (`adams where` prints its folder); a machine either links to a clone of it or uses the plugin, which Claude Code installs from a release. Change rules, lint lists, scripts, modules and router rows there and nowhere else, through a pull request.
- Never recreate a standalone copy of a module. A new capability becomes a new folder under `modules/` plus one row in the routing table.
- Code lives only in `scripts/` and `modules/*/scripts/`; guides point to it and never paste it. A lint list change is made in the script.
- After any edit run `adams selftest` (must print `selftest OK`) and say what was verified. A fresh clone must pass it, so nothing in the repo may depend on one person's machine.

## Hooks

- **Git guardrail:** `hooks/block-risky-git.py`, a `PreToolUse` hook on `Bash`. It blocks `git add -A`, `.` and `-u`, `git commit -a`, `reset --hard`, `clean -f`, `checkout .` and `restore .`, `branch -D` and force pushes (`--force-with-lease` and plain `git push` stay allowed). Run a blocked command yourself when it is really needed. Covered by `selftest`.
- **Reminder:** `hooks/adams_reminder.sh`, a `UserPromptSubmit` hook that reminds the agent to call Adams and run `adams check`. It prints once per session (marker file `adams-reminder-<session_id>` in the temp folder) and every time when no session id is given.
- **Updater:** `hooks/adams_update.sh`, a `SessionStart` hook that runs `adams update --auto` (once a day, release tags only, clean clones only, silent unless it updated; opt out with `ADAMS_AUTO_UPDATE=0`). A plugin install is updated by Claude Code instead.
- Hooks load at session start, so a new session is needed after `adams install`.

## Token cost

- `adams tokens` prints the estimated token cost (chars/4) of the always-on files, `SKILL.md` and every module guide.
- It is an estimate. `claude plugin details adams@adams` gives the exact count.
- Selftest caps the reminder, `ALWAYS.md` and `SKILL.md`; re-measure after editing any of them.

## Layout

```
adams/
  SKILL.md                      this router
  docs/COMPANIONS.md            companion skills, pipelines, input-to-checks table
  ALWAYS.md                     neutral always-on summary (Claude import, Copilot instructions)
  bin/adams                     the CLI: check, selftest, doctor, install, sync
  config/profiles/              shipped rule profiles (default, strict-ar)
  hooks/                        git guardrail, reminder, hooks.json for the plugin
  .claude-plugin/               plugin.json and marketplace.json
  scripts/check.py              one command, picks the checks by file type
  scripts/selftest.py           assert-based self-check, run after every edit
  scripts/track.py              lint and render .planning/track.md (revamp program tracker)
  hooks/adams_reminder.sh       UserPromptSubmit reminder
  VERSION, CHANGELOG.md         the version and its release notes
  scripts/tokens.py             `adams tokens`: est. token cost table
  scripts/update.py             version and updates; scripts/release.py cuts a release
  hooks/block-risky-git.py      PreToolUse guardrail for risky git commands
  modules/
    product-principles/GUIDE.md      how we think and decide; load before any judgment
      references/               conversion-psychology.md  funnel-map.md  dark-patterns.md
    humanize-writing/GUIDE.md  scripts/hzlint.py
    line-balance/GUIDE.md  scripts/{line_balance,wrap_sim}.py, web_balance.js  (canonical values table)
    deliverable-visual-qa/GUIDE.md  scripts/{title_check,lines,contrast,textlint,arlint}.py
    innovation-builder/GUIDE.md  references/
    seo-architect/GUIDE.md  references/  assets/
    senior-frontend/GUIDE.md  SaaS revamp program
      references/               page-standards.md  audit-scorecard.md  execution.md  track-template.md
    workflow/GUIDE.md           align (auto-ask), diagnose, handoff, retro (adapted from skills.sh)
    obsidian-vault-memory/GUIDE.md  references/
```
