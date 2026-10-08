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
- Optional modules live in the second plugin `adams-extras` (`plugins/adams-extras/`: its own `.claude-plugin/plugin.json`, `SKILL.md` router and `modules/`, listed in `.claude-plugin/marketplace.json`). It holds `innovation-builder`, `seo-architect` and `obsidian-vault-memory`; a module without tests is pruned there rather than into core. `scripts/release.py` bumps both manifests, so the two plugins always carry the same version. The core `SKILL.md` keeps one line pointing to it, and selftest fails if core scripts, hooks or `SKILL.md` name a moved module.
- Install: `/plugin install adams-extras@adams`. `adams install` and `adams sync` handle core only; a clone install uses `plugins/adams-extras` by hand.
- Code lives only in `scripts/` and `modules/*/scripts/`; guides point to it and never paste it. A lint list change is made in the script.
- Never name another skill, plugin or third-party project in any file; license notices for adapted material live only in `NOTICE` (selftest fails otherwise).
- After any edit run `adams selftest` (must print `selftest OK`) and say what was verified. A fresh clone must pass it, so nothing in the repo may depend on one person's machine.

## Hooks

- **Git guardrail:** `hooks/block-risky-git.py`, a `PreToolUse` hook on `Bash`. It blocks `git add -A`, `.` and `-u`, `git commit -a`, `reset --hard`, `clean -f`, `checkout .` and `restore .`, `branch -D` and force pushes (`--force-with-lease` and plain `git push` stay allowed). Run a blocked command yourself when it is really needed. Covered by `selftest`.
- **Reminder:** `hooks/adams_reminder.sh`, a `UserPromptSubmit` hook that reminds the agent to call Adams and run `adams check`. It prints once per session (marker file `adams-reminder-<session_id>` in the temp folder) and every time when no session id is given.
- **Updater:** `hooks/adams_update.sh`, a `SessionStart` hook that runs `adams update --auto` (once a day, release tags only, clean clones only, silent unless it updated; opt out with `ADAMS_AUTO_UPDATE=0`). A plugin install is updated by Claude Code instead.
- Hooks load at session start, so a new session is needed after `adams install`.

## Gates

Hard gates are hooks, so they hold even when the model forgets the prompt. All of them apply only inside a git work tree, never block on an internal error, and print their override as the last line of the deny message.

- **Align gate:** `hooks/adams_align_gate.py`, `PreToolUse` on `Edit`, `Write`, `MultiEdit` and `NotebookEdit`. The first code edit of a session is denied until `<repo>/.adams/decisions.md` is newer than that first call. Ask the open decisions (question tool, max 4, each with a recommendation), then record them with `adams decide "<decision>"`. For a clear, small, reversible task run `adams decide --small "<the one assumption>"`. `.md` and `.txt` files, `.adams/`, `.planning/`, paths outside a git work tree and the Claude scratchpad are never gated.
- **Verify record and Stop gate:** `hooks/adams_verify_record.py` (`PostToolUse` and `PostToolUseFailure` on `Bash`; `PostToolUse` also on `Edit`, `Write`, `MultiEdit` and `NotebookEdit`, where it appends the file path to `adams-touched-<session_id>`) records every test, build, typecheck or lint run with its result and a fingerprint of the working tree (`git diff HEAD` plus the names and sizes of untracked files). `hooks/adams_stop.py` blocks the stop once when this session edited source files and the tree differs from the latest green run. Nothing is blocked when the project has no detectable verification (`package.json` scripts, pytest, `go.mod`, `Cargo.toml`, `scripts/selftest.py` or `scripts/test.py`).
- **Commit gate:** `hooks/block-risky-git.py` also checks `git commit`. It denies a secret in the staged lines (AWS, `sk-`, private key, GitHub, Slack, Supabase `service_role` JWT; the value is masked), a staged `.env` or `.env.*` file other than `.env.example`, a message starting with `fix` or with a feature word (`feat`, `add `, `implement `) when source is staged without a test file, and staged source when the tree differs from the latest green run. The first commit of a session that stages source is also denied once with a review request (correct, safe, holds under load, tested, fast, lean); the retry in the same session passes (state `adams-review-<session_id>`). A denial lists every reason at once. Stage in one call and commit in another so the gate sees what is staged.
- **Opt-outs:** `ADAMS_GATES=0` turns off every gate, `ADAMS_VERIFY=0` only the verification checks (Stop and commit), `ADAMS_REVIEW=0` only the commit review, `ADAMS_STOP=0` only the text check. Set them in the environment before starting Claude Code, or run a command yourself with the `!` prefix.
- The Stop hook only looks at files this session wrote (the touched list), so a session is never blocked on files another live session edits in the same folder. Without a `session_id` or a touched list it never blocks. Foreign changes are not reported.
- Session state lives in the temp folder as `adams-align-<session_id>`, `adams-touched-<session_id>`, `adams-verify-<session_id>`, `adams-review-<session_id>` and `adams-router-<session_id>`.

## Context router

`hooks/adams_router.py` runs on `UserPromptSubmit` (stdout becomes context), `PostToolUse` for `Edit|Write|MultiEdit|Bash` and `PostToolUseFailure` for `Bash` (the JSON `hookSpecificOutput.additionalContext` field, with `hookEventName` set to the event). Claude Code sends a failed command only as `PostToolUseFailure`, so that registration is what lets the failed-test rule fire. It uses fixed regexes on the prompt, the edited path and the edit's old and new text (for `Write` on a manifest, the file at git `HEAD`); no model and no network. Rules and their texts are listed in the README table; the texts are `TEXT` in the script.

- Each rule fires once per session (`adams-router-<session_id>` holds the fired names and whether a test file was edited), at most two blocks per call in the order auth, dependency, tests, UI, prose, diagnose, plain, and the held back rule fires on a later matching call. A block is at most 600 characters. No match prints nothing.
- Files outside the project, `.adams/` and `.planning/` never match. The tests-first rule needs a git work tree with a detectable test command (the same detection as the verify gate).
- Dependency detection is line based per manifest. A bare package name with no version inside a `pyproject.toml` list is not seen; add a TOML parse if that matters.
- Opt out with `ADAMS_GATES=0` in the environment before starting Claude Code. Any internal error exits 0 silently. Selftest runs every rule, the once-per-session behavior, silence and garbage input.

## Stress mode

- `web_balance.js --stress` (and `--stress-all`) is described in `modules/line-balance/GUIDE.md`. `check.py` adds `--stress` for `.html` files and URLs by default; `-- --no-stress` removes it.
- Cost: every page and each of the two stress widths loads the page once as is and once per mutation (five loads), plus the normal scan. Above 20 pages stress is skipped with a WARNING line (it appears in the verdict) unless `--stress-all`.
- The hit type is `STRESS`; it counts in `FLAGGED` and in the per-type summary like the others, and the `--out` JSON carries `kind` and `reason`. A page that already breaks before any mutation reports it once as kind `as-is`.
- Detection lives in `stressPage` in `web_balance.js`. A new breakage rule goes there, with a case in selftest `web_routes` (a page that must flag and a page that must not).

## Scorecard

- `scripts/scorecard.py` (`adams scorecard`) and the tasks under `scorecard/` are described in `scorecard/README.md`. `--dry-run` runs in selftest: every fixture builds, every check fails on the untouched fixture and passes on its golden solution.
- `--run` spends money. It prints an estimate first (8 cases at $0.15 to $0.70 each), stops before a case that could pass `--max-cost` (default 6), and passes `--max-budget-usd` to each case. Results land in `scorecard/results/` (git-ignored).
- Run it per release, with `--runs 3`, and keep the JSON next to the release notes. Do not run it from CI: it uses a personal Claude account and its real configuration.
- A new task needs `prompt.md`, `fixture/`, `check.py` and a `golden/` solution; the dry run refuses a check that cannot fail or cannot pass.

## Token cost

- `adams tokens` prints the estimated token cost (chars/4) of the always-on files, `SKILL.md` and every module guide.
- It is an estimate. `claude plugin details adams@adams` gives the exact count.
- Selftest caps the reminder, `ALWAYS.md` and `SKILL.md`; re-measure after editing any of them.

## Layout

```
adams/
  SKILL.md                      this router
  docs/PIPELINES.md              pipelines, input-to-checks table
  ALWAYS.md                     neutral always-on summary (Claude import, Copilot instructions)
  bin/adams                     the CLI: check, selftest, doctor, install, sync
  config/profiles/              shipped rule profiles (default, strict-ar)
  hooks/                        git guardrail, reminder, hooks.json for the plugin
  .claude-plugin/               plugin.json and marketplace.json
  scripts/check.py              one command, picks the checks by file type
  scripts/selftest.py           assert-based self-check, run after every edit
  scripts/scorecard.py          `adams scorecard`: real-task scorecard runner (scorecard/ holds the tasks)
  scorecard/                    tasks/<name>/{prompt.md,fixture,check.py,...}, common.py, README.md
  scripts/track.py              lint and render .planning/track.md (revamp program tracker)
  hooks/adams_reminder.sh       UserPromptSubmit reminder
  VERSION, CHANGELOG.md         the version and its release notes
  scripts/tokens.py             `adams tokens`: est. token cost table
  scripts/update.py             version and updates; scripts/release.py cuts a release
  hooks/block-risky-git.py      PreToolUse guardrail for risky git commands, commit gate
  hooks/adams_router.py         context router (prompt, edit and failed-test rules)
  modules/
    product-principles/GUIDE.md      how we think and decide; load before any judgment
      references/               conversion-psychology.md  funnel-map.md  dark-patterns.md
    humanize-writing/GUIDE.md  scripts/hzlint.py
    line-balance/GUIDE.md  scripts/{line_balance,wrap_sim}.py, web_balance.js  (canonical values table)
    deliverable-visual-qa/GUIDE.md  scripts/{title_check,lines,contrast,textlint,arlint}.py
    senior-frontend/GUIDE.md  SaaS revamp program
      references/               page-standards.md  audit-scorecard.md  execution.md  track-template.md
    workflow/GUIDE.md           align (auto-ask), complete output; references/ holds diagnose, handoff, retro
  plugins/adams-extras/         optional second plugin: .claude-plugin/plugin.json, SKILL.md router
    modules/
      innovation-builder/GUIDE.md  references/
      seo-architect/GUIDE.md  references/  assets/  scripts/ai_search_audit.py
      obsidian-vault-memory/GUIDE.md  references/
```
