<p align="center">
  <img src="docs/assets/banner.png" alt="Adams: checks every draft before it ships. A paragraph with one orphan word, before and after balancing." width="100%">
</p>

<p align="center">
  <a href="https://github.com/UpgradIQ/adams/actions/workflows/selftest.yml"><img src="https://github.com/UpgradIQ/adams/actions/workflows/selftest.yml/badge.svg" alt="selftest"></a>
  <a href="https://github.com/UpgradIQ/adams/releases/latest"><img src="https://img.shields.io/github/v/release/UpgradIQ/adams?color=14202B&label=release" alt="Latest release"></a>
  <img src="https://img.shields.io/badge/license-MIT-12805C" alt="MIT license">
  <img src="https://img.shields.io/badge/Claude%20Code-skill%20and%20plugin-14202B" alt="Claude Code skill and plugin">
  <img src="https://img.shields.io/badge/Copilot%20CLI-skill-14202B" alt="Copilot CLI skill">
</p>

One skill for Claude Code and GitHub Copilot CLI that makes the work better on any project: text that does not read as AI-written, layout and visual checks, a workflow for planning and debugging, shared product principles, and standards for building SaaS. It runs its checks on its own, so nobody has to remember to ask, and it updates itself.

Created by Adam Hafez at [UpgradIQ](https://github.com/UpgradIQ). License: MIT, see LICENSE and NOTICE.

## What is new in 2.0

- **It updates itself.** A clone follows release tags and updates quietly once a day; plugin users switch on auto-update once.
- **Versioned releases** with a changelog and a GitHub Release for every version.
- **`adams check --changed`** checks only the files you changed, in a pull request or in CI.
- **`adams init`** gives a whole project one shared rule profile.

Installed 0.1.0? It had no updater: run `git -C ~/adams pull` once (or `claude plugin marketplace update adams` for the plugin). The full list is in [CHANGELOG.md](CHANGELOG.md).

## See it work

A draft full of AI tells fails. The same draft, rewritten, passes. Both runs are real output of `adams check`.

<img src="docs/assets/demo.png" alt="Terminal: adams check flags eight blocking phrases in a draft, then reports CLEAN after the rewrite." width="100%">

## How it works

<img src="docs/assets/how-it-works.png" alt="Four steps: you work, Adams loads the module the task needs, adams check picks the right check for each file or URL, and every hit is fixed and checked again until clean." width="100%">

Adams loads on matching tasks, runs the check that fits what you built or wrote, fixes every hit and checks again. Nothing is called by hand, and nothing is reported as passed unless it ran.

## What gets checked

<img src="docs/assets/checks.png" alt="Six check types: writing check for md and txt, layout check for pdf, deck check for pptx, document check for docx, page check for html, and site check for https URLs." width="100%">

## Stress mode and the real-task scorecard

`adams check` on an `.html` file or a URL also stresses the layout at 375 and 1440: it makes a copy of the live page with twice the words, a 40 character unbroken string, 9-digit numbers and blanked lists, and reports `STRESS` where the layout breaks (sideways scroll, text past its box, clipped text, overlap). Skip it with `adams check page.html -- --no-stress`.

`adams scorecard` measures the plugin on eight small programming tasks in throwaway git repos, scored by hidden deterministic checks (asks before building, regression test, tests first, no scope creep, no committed secret, verified before done, layout that holds, no new dependency). `adams scorecard --dry-run` makes no model calls and runs in selftest; `--run` uses your real Claude account and configuration and costs about $1.20 to $5.60 for all eight tasks once. Details in [`scorecard/README.md`](scorecard/README.md).

## What runs automatically

| When | What | Opt out |
|---|---|---|
| Every prompt | a short reminder: align first, run `adams check` on deliverables | remove the plugin or its hook |
| Task start, and when the work drifts | asks the open decisions with a recommendation for each, records them in `.adams/decisions.md` | skipped for small, reversible tasks |
| Session start | reloads `.adams/decisions.md` for the project; checks for a new release once a day (clone installs) | n/a |
| Before a code edit | denies the first code edit of a session until the open decisions are asked and recorded with `adams decide` (`--small` for a small task) | `ADAMS_GATES=0` |
| After a test, build, typecheck or lint run | records the result and a fingerprint of the working tree | `ADAMS_GATES=0` |
| Before the agent stops | runs the text check on changed `.md` and `.txt` files; blocks once if code changed since the last green verification | `ADAMS_STOP=0` (text), `ADAMS_VERIFY=0` (code) |
| Before `git commit` | denies a staged secret or `.env` file, a `fix` or feature (`feat`, `add`, `implement`) commit without a test, source changed since the last green verification, and the first commit of a session that stages source until the diff is reviewed (correct, safe, holds under load, tested, fast, lean) | `ADAMS_GATES=0`, `ADAMS_VERIFY=0` (verification), `ADAMS_REVIEW=0` (review) |
| Every prompt and every edit | the context router adds a short guidance block when plain rules match, once per rule per session (table below) | `ADAMS_GATES=0` |

Every deny message ends with its override. Hooks make no network calls except the daily release check. Behavior tests live in `evals/` (`claude plugin eval`, costs API usage). If your app does not load marketplace plugins, `adams install --link` links the skill and registers the hooks directly.

### The context router

`hooks/adams_router.py` matches the prompt, the edited path or a failed test run with fixed rules (no AI, no network) and adds a block of at most 600 characters. Each rule fires once per session, at most two blocks per call, and nothing is added when no rule matches.

| Trigger | What Adams adds |
|---|---|
| Prompt says broken, error, bug, failing, crash, not working, exception, regression (or the Arabic equivalents), or a test or build command fails | diagnose: reproduce, minimise, one hypothesis at a time, fix, regression test, no blind retries |
| "I don't understand" or "explain simply" (or the Arabic equivalents) | restate the last answer short and plain, in the user's language |
| Editing a path with auth, session, login, password, token, jwt, oauth, middleware, proxy, `.env`, secret, permission, role, rls or policy | security checklist: input validation, server-side authorization, no secrets in client code, rate limits, constant-time compares, cookie flags, row level security |
| Adding a dependency to `package.json`, `requirements*.txt`, `pyproject.toml`, `go.mod` or `Cargo.toml` | does the platform or an installed dependency cover it, what does it cost, say so to the user |
| UI files (`.tsx`, `.jsx`, `.vue`, `.svelte`, `.css`, `.scss`, `.html`) | `adams check` at 375, 768 and 1440, long text, empty and error states, focus, RTL |
| First source edit with no test edited yet, in a project with a test setup | one failing test first, then the implementation, through public interfaces |
| Published copy (`README`, `docs/`, posts, `content/`) | minimum effective edit, keep the author's voice, list what changed |

## Modules

| Module | Use it for |
|---|---|
| `product-principles` | how to decide: truth over wishes, focus, ethical persuasion, no dark patterns |
| `humanize-writing` | text that does not read as AI-written, in English and Arabic (26 English tells plus Arabic style rules) |
| `line-balance`, `deliverable-visual-qa` | no orphan words, equal cards, contrast, RTL, for PDFs, decks, docs, websites and dashboards |
| `workflow` | auto-ask with recommendations (align), diagnose bugs with a feedback loop, handoff, retro, complete output |
| `senior-frontend` | Next.js, Supabase, Stripe, Sentry, a security checklist, a SaaS revamp program with a tracker |
| `seo-architect`, `innovation-builder`, `obsidian-vault-memory` | SEO site blueprints, WordPress canvases and worksheets, an Obsidian vault as memory |

## Install

You need Python 3.9+, Node 18+ and git. LibreOffice is optional (pptx and docx checks).

### Claude Code plugin

    /plugin marketplace add UpgradIQ/adams
    /plugin install adams@adams

### Any terminal, Claude Code and Copilot CLI together

This works in Warp, iTerm or any shell.

    git clone https://github.com/UpgradIQ/adams.git ~/adams
    ~/adams/bin/adams install --dry-run     # shows exactly what it will change
    ~/adams/bin/adams install
    export PATH="$HOME/.local/bin:$PATH"    # add to your shell profile
    adams sync                              # Copilot instructions
    adams doctor                            # what is missing and how to fix it

Start a new Claude Code or Copilot session afterwards (skills and hooks load at session start). Use one install method, not both: if the plugin is enabled, `adams install` skips the skill link and the hooks on its own. `adams uninstall` removes exactly what `install` added.

## Staying up to date

<img src="docs/assets/updates.png" alt="Three steps: a release is tagged, your session starts and Adams looks for a newer tag, and a clean clone moves forward and says what is new." width="100%">

**Plugin install.** Claude Code does not auto-update third-party marketplaces by default. Turn it on once: run `/plugin`, open the Marketplaces tab, choose `adams`, and enable auto-update. Or set it in your settings:

    {
      "extraKnownMarketplaces": {
        "adams": { "source": { "source": "github", "repo": "UpgradIQ/adams" }, "autoUpdate": true }
      }
    }

Update by hand any time with `claude plugin marketplace update adams` and `claude plugin update adams@adams`, then restart the session. The skill appears as `adams:adams`; `/plugin` lists what is installed.

**Clone install.** Nothing to do: a session-start hook runs `adams update --auto` at most once a day. It follows release tags (never the main branch), updates only a clean clone, only fast-forwards, and prints what is new. Update now with `adams update`; ask without changing anything with `adams update --check`. Opt out with `ADAMS_AUTO_UPDATE=0`.

**A whole team.** Put the marketplace and the plugin in the project's `.claude/settings.json` and commit it, so everyone on the project gets Adams and its updates:

    {
      "extraKnownMarketplaces": {
        "adams": { "source": { "source": "github", "repo": "UpgradIQ/adams" }, "autoUpdate": true }
      },
      "enabledPlugins": { "adams@adams": true }
    }

Updates run code from this repository, so they follow the same trust you gave when you installed it. Releases are tagged by the maintainers and listed on the [Releases page](https://github.com/UpgradIQ/adams/releases).

## Use

Nothing to call. You can also run it by hand: `adams check report.pdf`, `adams check article.md`, `adams check https://example.com`. `adams check --changed` checks only what you changed. `adams init` sets the rule profile for a project. `adams version` and `adams selftest` do what they say.

## Scheduled audits

Run a weekly check on a staging URL by scheduling one prompt. With `/schedule` it becomes a cloud routine (it needs the Adams plugin in the routine's environment and a staging URL that is reachable from the internet). With the `loop` skill (`/loop 7d <prompt>`) it runs locally, but only while that Claude Code session stays open. Both spend API usage on every run.

```
Run `adams check https://staging.example.com` and `python3 modules/seo-architect/scripts/ai_search_audit.py https://staging.example.com`. Report each FLAGGED or FAIL line with the page and the fix, say what was not checked, and stay silent if both are clean.
```

## Profiles and per-project settings

Rules are grouped into profiles. `default` carries only universal AI-writing tells. `strict-ar` adds Arabic style, register and post-layout rules. Pick one per project in `.adams/config.json` (`{"profile": "strict-ar"}`) or per person in `~/.config/adams/config.json`. Your own preferences go in `~/.config/adams/profiles/<name>.json` (a profile may `extends` another) and are never part of this repository.

## What it touches (read before installing)

`adams install` adds symlinks and two hooks to `~/.claude/settings.json` (with a backup). The hooks are local scripts: a guardrail that blocks risky git commands such as `git add -A`, `reset --hard` and force pushes (plain `git push` is allowed), and a reminder to run the checks. On first use the layout checkers install pinned dependencies (Playwright and Chromium, pdfplumber, Pillow); set `ADAMS_AUTO_INSTALL=0` to forbid that. There is no telemetry. See [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). `adams selftest` must print `selftest OK`; CI runs it on a fresh clone. The images in `docs/assets` are rendered from `docs/visuals/src` with `node docs/visuals/render.js`.
