---
name: adams
description: "Invoke automatically, without being asked, on any matching task. Adams, the all-in-one toolkit, ten modules. Mindset: product-principles (load before planning, deciding, designing, auditing, advising). Writing: humanize-writing (any text written for or published under a person or brand, Arabic and English). Layout QA: line-balance and deliverable-visual-qa (decks, PDFs, docs, images with text, web pages, sites, dashboards, before delivery). SaaS revamp: audit or upgrade a SaaS (UI/UX/CX, ethical conversion, onboarding, pricing, admin, docs), tracked in .planning/track.md. Build: innovation-builder (WordPress canvas, worksheet, scorecard blocks), seo-architect (keyword research to static SEO sites), senior-frontend (Next.js, React, TypeScript, Tailwind, Supabase, Stripe, Vercel, Sentry). Workflow: align (asks and recommends automatically at the start and on drift), diagnose bugs, handoff, retro. Memory: obsidian-vault-memory."
---

# Adams

One skill, ten modules. Read this page, pick the module(s), then load only that module's `GUIDE.md`. Never load all of them.

## Route by task

| The task is | Load | Notes |
|---|---|---|
| Planning, deciding, designing, auditing, scoring a plan, advising, or any product or business judgment | `modules/product-principles/GUIDE.md` | Load first, before any other module. `ALWAYS.md` is its always-on summary. |
| **Start of any non-trivial task (automatic)**, drift while building, stress-testing a plan ("challenge this", "poke holes"), diagnose something broken, failing or slow, write a session handoff, or run a retro on a bad session | `modules/workflow/GUIDE.md` | Adapted from skills.sh (mattpocock/skills). Load `product-principles` first for the judgment calls. |
| Any text written for or published under a person or brand (LinkedIn post, reply, DM, email, script, caption, metadata, playbook), Arabic or English | `modules/humanize-writing/GUIDE.md` | Contains the language rules and the `hzlint.py` lint. Mandatory before delivery. |
| Any file with a fixed layout (pptx, PDF, docx, HTML page, image with text) | `modules/line-balance/GUIDE.md` then `modules/deliverable-visual-qa/GUIDE.md` | Scripts: `modules/line-balance/scripts/`. Line balance first, full QA gate last. |
| Fix or check text on a website, web app, SaaS User or Admin dashboard, or academy (line balance, orphan words, uneven cards, dead words) | `modules/line-balance/GUIDE.md` section "Websites and apps" | `scripts/web_balance.js` (Playwright): crawl or URL list, test logins per role, widths 375/768/1440, RTL. Pilot one page first. |
| Check Arabic text for singular address, literal-translation traps or odd phrasing (script, speaker notes, playbook, metadata-AR) | `modules/deliverable-visual-qa/GUIDE.md` section 7b, run `scripts/arlint.py FILES...` | Run it together with `hzlint.py` (humanize-writing), never instead of it. Every odd phrase a reviewer flags goes into `TRAPS` in `arlint.py`. |
| Canvas, worksheet, framework, matrix, scorecard, planner as a WordPress HTML block | `modules/innovation-builder/GUIDE.md` | `references/` holds the spec contract and the 230-template catalog. |
| Keyword opportunities, programmatic static SEO site, internal linking plan, content briefs | `modules/seo-architect/GUIDE.md` | Load its `references/` files at the step the guide names. |
| AI search readiness (GEO/AEO): llms.txt, AI crawlers, schema, citable pages | `modules/seo-architect/GUIDE.md` section "AI search (GEO/AEO)" | Run `scripts/ai_search_audit.py URL_OR_FOLDER`; facts in `references/ai-search.md`. |
| Next.js, React, TypeScript, Tailwind, shadcn/ui, Supabase, Stripe, Vercel, Sentry code | `modules/senior-frontend/GUIDE.md` | Spec-first: Server Components default, measured bundles, typed Supabase and Stripe. |
| Revamp or audit a SaaS (UI/UX/CX, conversion, onboarding, pricing, dashboards, admin, docs), plan or track its execution | `modules/product-principles/GUIDE.md` (references `conversion-psychology.md`, `funnel-map.md`, `dark-patterns.md`) + `modules/senior-frontend/GUIDE.md` section "SaaS revamp program" and its `references/` | `scripts/track.py` lints and renders `.planning/track.md`. Ethical persuasion only. Canonical layout values: `line-balance/GUIDE.md`. |
| Save to, search or read the Obsidian vault, "remember this", "second brain" | `modules/obsidian-vault-memory/GUIDE.md` | `references/endpoints.md` and `setup-guide.md`. |

Inside any module, a mention of "the humanize-writing skill", "the deliverable-visual-qa skill" or "the line-balance skill" means the module of that name here. Relative paths (`references/`, `assets/`, `scripts/`) resolve inside that module's folder.

## Companion skills (installed separately, Adams routes to them instead of copying them)

Adams does not duplicate what a good skill already does. For these areas load the named skill after the Adams module that applies, and let Adams' rules win on any conflict.

| Area | Skills | Adams rule that wins |
|---|---|---|
| Visual design and UI polish | `high-end-visual-design`, `frontend-design`, `impeccable`, `ui-ux-pro-max`, `design-review`, `motion-designer` | `line-balance` canonical table, `product-principles` (no dark patterns) |
| Marketing copy, CRO, pricing, SEO audits | `copywriting`, `marketing-psychology`, `programmatic-seo`, `seo-audit`, `ai-seo`, `cold-email`, `linkedin-writer` | `humanize-writing` lint and `product-principles` (truth over wishes) |
| Frontend and database craft | `nextjs-best-practices`, `react-best-practices`, `shadcn`, `supabase-postgres-best-practices`, `web-perf` | `senior-frontend` standards |
| Charts and KPI dashboards | `kpi-dashboard-design`, `dataviz` | `line-balance` for any text in them |
| Planning, TDD, verification | `brainstorming`, `writing-plans`, `tdd`, `verification-quality` | `workflow` section 3 |
| Debugging and incidents | `investigate`, `retro` | `workflow` sections 2 and 5 |

**Missing a capability?** Run `find-skills` (it searches skills.sh) before building one. Installing a third-party skill is a download from outside: name the skill, its source and size to the user and ask first, and read its audit results on skills.sh and its files before you propose it.

## Pipelines (the modules chain, run them in this order)

```
text only      write --> humanize-writing --> deliver
laid-out file  write --> humanize-writing --> build --> line-balance --> deliverable-visual-qa --> deliver
course lesson  (a private add-on skill builds it) --> humanize-writing --> line-balance --> deliverable-visual-qa --> deliver
SEO site       seo-architect --> senior-frontend (build) --> deliverable-visual-qa (if a visual deliverable)
```

## Standing rules every module shares

- Language: code, commits, docs, plans, reports and UI copy are English; chat follows the user's language; content requested in Arabic (posts, scripts, AR metadata) follows humanize-writing section 1. The rules work in any language: Arabic and English get full word lists, other languages get the structural checks plus an explicit "not covered" notice (`hzlint.py` prints it). Never claim a pass for something a check could not measure.
- Layout: one set of values for every project, in the canonical table of `modules/line-balance/GUIDE.md`. Fix by rewording, never by shrinking the font.
- Align first, automatically: on any non-trivial task, read the project docs, then ask the user the open decisions with a recommended best practice for each, and ask again when the work drifts (`modules/workflow/GUIDE.md` section 1). Never wait to be told "ask me"; skip it only for clear, small, reversible tasks.
- Done means proof: say what was checked and the result (for example `FLAGGED 0`, `0 BLOCK hits`). If something was not verified, say so.
- Scratch output (renders, lint output) goes in the scratchpad, never in the user's own folders.

## Auto-run: smart, no asking

Adams runs itself inside normal conversations. Nobody has to call it, name it or approve it.

**One command picks the checks for you:** `adams check FILE_OR_URL ...` (or `python3 <skill folder>/scripts/check.py FILE_OR_URL ...` when the command is missing) (exit 1 if anything is flagged, last line `ADAMS CHECK: CLEAN` or `FLAGGED`).

| Input | What it runs automatically |
|---|---|
| `.txt` / `.md` | `hzlint` (mode from the file name and headings) plus `arlint` when the text has Arabic |
| `.pdf` | `line_balance` and `title_check` |
| `.pptx` | `textlint` over slide text and speaker notes, then rendered to PDF with LibreOffice and checked like a PDF |
| `.docx` | rendered to PDF with LibreOffice, then checked like a PDF |
| `.html` | serves it on a temporary local port, then `web_balance` at 375, 768, 1440 |
| `http(s)://` URL (site, dashboard, academy) | `web_balance --crawl --max 10`; pass other flags after `--` |

When to run it, without being asked: before delivering any text for a person or brand; after building or changing a pptx, docx (render to PDF first), PDF, image with text, web page, UI or dashboard; whenever Arabic text is in a deliverable. Scope is the files changed in this task.

- Pick the cheapest check that fits. Do not run a check that cannot apply (pure chat, no layout) and do not re-run a file that has not changed since it last passed.
- Fresh eyes: for Arabic text, published posts and scripts, also spawn a separate reviewer agent with the text alone and the prompt in `modules/humanize-writing/fresh-eyes-prompt.md` (`check.py` prints this reminder after any text check). If no agent is available, say so in the report.
- Dependencies are pre-approved for this skill: scripts install what they need (Playwright and Chromium, `pdfplumber`, `pillow`) on first run. Do not ask first. This overrides the cost and dependency gate for Adams tooling only. If an install fails (no network, locked machine), say so plainly and do not work around it.
- Fix every BLOCK or FLAGGED hit at the source, re-run until `CLEAN`, then report the result in one line. If a check was not run, say so.
- Never ask the user to run a check or to install anything for it.

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
- **Reminder:** `hooks/adams_reminder.sh`, a `UserPromptSubmit` hook that reminds the agent to call Adams and run `adams check`.
- **Updater:** `hooks/adams_update.sh`, a `SessionStart` hook that runs `adams update --auto` (once a day, release tags only, clean clones only, silent unless it updated; opt out with `ADAMS_AUTO_UPDATE=0`). A plugin install is updated by Claude Code instead.
- Hooks load at session start, so a new session is needed after `adams install`.

## Layout

```
adams/
  SKILL.md                      this router
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
