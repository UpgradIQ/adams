# Adams operations

Moved out of `SKILL.md` to keep the always-loaded router small.

## Install and use on any machine (Claude Code and Copilot CLI, Warp or any terminal)

- `adams install` links the skill for Claude Code (`~/.claude/skills/adams`) and Copilot CLI (`~/.copilot/skills/adams`), puts `adams` on the PATH (`~/.local/bin`) and registers the two hooks. `adams doctor` reports what is missing and how to fix it; `adams uninstall` removes exactly what install added; `adams sync` writes the Copilot instructions (`ALWAYS.md`, plus an optional personal overlay).
- Claude Code reads `ALWAYS.md` through an `@` import in `~/.claude/CLAUDE.md` (add `@<folder printed by adams where>/ALWAYS.md`). Copilot has no prompt hook, so its instructions file does that job.
- Scripts are plain Python and Node and resolve their own folder, so they run the same from either tool and from CI.
- Where a module says "spawn a reviewer agent", Copilot uses its own subagent if one is available; otherwise do the fresh-eyes pass in a separate step and say so.

## Profiles: team default and personal rules

`hzlint.py` and `check.py` read an active profile (rule groups on or off). Order: `ADAMS_PROFILE`, then the nearest `.adams/config.json` upward from the working folder (`{"profile": "strict-ar"}`), then `~/.config/adams/config.json`, then the plugin option `profile` (reaches hooks as `CLAUDE_PLUGIN_OPTION_PROFILE`), then `default`. Profiles are `<name>.json` files in `~/.config/adams/profiles/` or `config/profiles/` and may `extends` another. Shipped: `default` (universal AI-writing tells only) and `strict-ar` (Arabic style, register and post layout). The commit gate reads the same profile for `groups.forbid_coauthor` (see the commit gate above). Personal rules, such as religious-word or dash bans, live in a personal profile and `~/.config/adams/personal.md`, never in this repo.

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
- **Verify record and Stop gate:** `hooks/adams_verify_record.py` (`PostToolUse` and `PostToolUseFailure` on `Bash`; `PostToolUse` also on `Edit`, `Write`, `MultiEdit` and `NotebookEdit`, where it records the file path and the sha1 of its content right after the write in `adams-touched-<session_id>`, as `{path: sha1}`) records every test, build, typecheck or lint run with its result and a fingerprint of the working tree (`git diff HEAD` plus the names and sizes of untracked files). `hooks/adams_stop.py` blocks the stop once when this session edited source files and the tree differs from the latest green run. Nothing is blocked when the project has no detectable verification (`package.json` scripts, pytest, `go.mod`, `Cargo.toml`, `scripts/selftest.py` or `scripts/test.py`).
- **Commit gate:** `hooks/block-risky-git.py` also checks `git commit`. It denies a secret in the staged lines (AWS, `sk-`, private key, GitHub, Slack, Supabase `service_role` JWT; the value is masked), a staged `.env` or `.env.*` file other than `.env.example`, a message starting with `fix` or with a feature word (`feat`, `add `, `implement `) when source is staged without a test file, and staged source when the tree differs from the latest green run. The first commit of a session that stages source is also denied once with a review request (correct, safe, holds under load, tested, fast, lean); the retry in the same session passes (state `adams-review-<session_id>`). A denial lists every reason at once. Stage in one call and commit in another so the gate sees what is staged.
  - **Co-Authored-By trailer (profile setting, off by default):** a profile with `"groups": {"forbid_coauthor": ["Claude", "noreply@anthropic.com"]}` makes the commit gate deny a `git commit` whose message holds a `Co-Authored-By:` line that contains any listed substring (case-insensitive). The message is read from `-m` and `--message`, a heredoc inside `-m "$(cat <<EOF ...)"`, `-F file`, and from `HEAD` for `git commit --amend --no-edit`; a message typed in the editor is not seen. The denial says: "This profile forbids that Co-Authored-By trailer in commits; remove the line and commit again." Other trailers (a human co-author) pass. Turn it on in your own profile (`~/.config/adams/profiles/<name>.json`, picked as described under Profiles); `groups` merge through `extends`, so a team can set it in a shared profile once. The shipped profiles do not set it. `ADAMS_GATES=0` turns it off with the rest of the commit gate.
- **Agent deviation gates** (`hooks/adams_deviation_gate.py`, `PreToolUse` on `Bash`, `Edit`, `Write`, `MultiEdit` and `NotebookEdit`, 5 second timeout; the commit and shell parts live in `hooks/block-risky-git.py`, the Stop parts in `hooks/adams_stop.py`). They stop an agent from reaching green by weakening the referee. A denial lists every reason and ends with its override. Each gate only looks at what a call adds: a pattern that was already in the file is left alone, and the Adams source itself (`hooks/`, `scripts/` in a work tree that holds `hooks/adams_gates.py`) is exempt from the pattern checks. For a shell command the targets come from `bash_targets` (any extension), so a command that only reads a path it also writes elsewhere (`cp ~/.claude/settings.json /tmp`) counts as touching it.
  - **Test tampering:** a test file (`tests/`, `__tests__/`, `test_*.py`, `*.test.*`, `*.spec.*`) that gains `.skip(`, `.only(`, `xit(`, `xdescribe(`, `xtest(`, `it.todo`, `@pytest.mark.skip` (not `skipif`), `pytest.skip(`, `@unittest.skip`, `t.Skip(` or `#[ignore]`; a tracked test file or test folder taken away by `rm`, `git rm` or `mv` (a move to another test path is a rename and passes); a `Write` that empties a test file; an edit whose new text has fewer assertions (`assert`, `expect(`, `should.`, `assertEqual` and the like) than the old text. Fix the code, not the test. A real refactor that merges assertions needs the user.
  - **Silencing errors:** `@ts-ignore`, `@ts-nocheck`, `@ts-expect-error` with fewer than 10 characters of reason on the same line, `eslint-disable` in any form, `# type: ignore`, `# noqa`, `//nolint`, a new `: any` or `as any` in `.ts` and `.tsx`, and config edits that set `strict` and the `noImplicit*` and `noUnused*` flags to false, turn an eslint rule off, or grow an ignore list in ruff, mypy, flake8, setup.cfg or pyproject. The agent must ask the user and give the written reason; there is no automatic exception.
  - **Gaming checks:** `.github/workflows/*`, `.gitlab-ci.yml`, `.circleci/config.yml`, `.nycrc*`, `.c8rc*`, `.coveragerc`, `codecov.yml`, `lighthouserc*`, `budget.json`, snapshots (`__snapshots__/`, `*.snap`, `jest -u`, `vitest -u`, `--update-snapshots`), `.adams/config.json`, outside the Adams repo `scripts/selftest.py`, and threshold lines in `jest.config.*`, `vitest.config.*`, `playwright.config.*`, `package.json`, `pyproject.toml`, `setup.cfg`, `tox.ini` and `pytest.ini`. They open for the whole session once a prompt of the user contains `ci`, `workflow`, `threshold`, `snapshot` or `selftest` (the router stores only those words in `adams-router-<session_id>`, never the prompt). Without a session id they stay closed. The user's own Adams config under `~/.config/adams` is covered by the self-disabling gate, which has no prompt exception.
  - **Self-disabling:** a command that sets `ADAMS_GATES=0`, `ADAMS_VERIFY=0`, `ADAMS_STOP=0` or `ADAMS_REVIEW=0` (outside the Adams repo), and any write or delete of `~/.claude/settings*.json`, `~/.claude/CLAUDE.md`, `~/CLAUDE.md`, `~/.config/adams/**`, `~/.claude/plugins/**`, and of a project `.claude/settings*.json` when the change mentions hooks. Only the user can change these; inside the Adams repo editing its own source is allowed.
  - **Scope:** `adams decide --scope "src/**,lib/"` appends `- YYYY-MM-DD HH:MM:SS: scope: src/**,lib/` to `.adams/decisions.md`. The deviation gate fixes each session's start at its first call (state `adams-session-<session_id>`); the latest scope line written at or after that start is the session's scope. A write or a staged file outside it is denied with the scope shown; tests, docs (`.md`, `.txt`, `docs/`), `.adams/` and `.planning/` stay open. No scope line, or only an older one: no effect. Globs use `fnmatch` (`*` also crosses `/`, so `src/*` equals `src/**`); a trailing `/` means a folder prefix. A session already running when the line is written is limited too. Widen it with a new `--scope` line.
  - **Destructive commands:** `block-risky-git.py` adds `git commit --no-verify` and `-n`, `git push --no-verify`, `--force-with-lease` to an explicit `main` or `master` ref (plain `--force`, `-f` and `+ref` were already denied), `rm -r` on the repo root, `/`, the home folder or a tracked folder (`node_modules`, `dist`, `build`, `.next`, `coverage`, `tmp` and `scratch` are fine), `DROP TABLE|DATABASE|SCHEMA` and `TRUNCATE` when a database client (`psql`, `mysql`, `sqlite3`, `supabase`, `prisma` and the like) is a command word, `supabase db reset` and `prisma migrate reset`. A migration file written with `cat > m.sql` or searched with `grep` passes. The git rules stay on with `ADAMS_GATES=0`; the new shell rules go off.
  - **Leftovers:** at `git commit` the added lines of staged source are scanned: `console.log(` (allowed under `scripts/`, `bin/`, `cli*`, `tools/` and in tests), `debugger;`, a line starting with `print(` in Python (same allowances), a new `TODO`, `FIXME` or `XXX`, and in non-test, non-fixture, non-story paths `lorem ipsum`, `John Doe`, `example@example.com`, `test@test.com`, `Math.random()` on a line that assigns data, and arrays named `mock*`, `fake*` or `dummy*`. Each hit is listed as `file:line`.
  - **Small-task abuse:** the Stop hook reads the decisions recorded since the session start. If all of them are `small task:` and the session wrote more than 3 source files or more than 80 changed lines (`git diff --numstat HEAD` over the touched files, plus the lines of new files), it blocks once per session (state `adams-smallstop-<session_id>`) and asks for a proper alignment: questions with recommendations, then `adams decide`.
  - **Unsourced numbers:** the Stop hook reads the last assistant text of the `transcript_path` (skipped above 50 MB). A figure counts as a claim only when it is a number followed by `%`, `x`, `ms`, `tests`, `errors`, `passed` or `failed`, an `N/N pass`, `score N`, `all tests pass`, `FLAGGED 0` or `CLEAN` (capitals). It is backed when the same number or word appears in a Bash command or Bash output of the session or in what the user typed (system reminders are ignored), or, for `all tests pass`, `N/N pass` and `0 errors`, when a verification run of the session was green. Otherwise it blocks once per session (state `adams-numstop-<session_id>`). It only runs for sessions that wrote a file.
  - **How to override:** set the variable in the environment before starting Claude Code (`ADAMS_GATES=0`; `ADAMS_STOP=0` also covers the figures check). The agent cannot do it for you, and it is told so. For the referee files, say so in a prompt (for example "update the CI workflow") and the agent can proceed; for a silencing directive or a loosened config, tell the agent the reason in writing and make the change yourself with the `!` prefix.
- **Opt-outs:** `ADAMS_GATES=0` turns off every gate, `ADAMS_VERIFY=0` only the verification checks (Stop and commit), `ADAMS_REVIEW=0` only the commit review, `ADAMS_STOP=0` only the text check. Set them in the environment before starting Claude Code, or run a command yourself with the `!` prefix.
- The Stop hook only looks at files this session wrote (the touched state), so a session is never blocked on files another live session edits in the same folder. Without a `session_id` or a touched state it never blocks. Foreign changes are not reported.
- **Own-write attribution:** a file counts as this session's change only while its current content hash equals the one recorded right after this session's last write (`mine(sid)` in `hooks/adams_gates.py`, used by the Stop text, verification and small-task checks). If another session or a tool changes the file afterwards, it is no longer this session's until this session writes it again, which records the new hash. A file this session deleted counts as its own; a file another writer deleted does not. Touched state written by an older version (a plain list of paths) still loads and counts every path until the next write migrates it. Shortcut: a formatter or other command run outside the edit tools that rewrites this session's file also drops it from the set.
- Session state lives in the temp folder as `adams-align-<session_id>`, `adams-touched-<session_id>`, `adams-verify-<session_id>`, `adams-review-<session_id>`, `adams-router-<session_id>` (also the referee words the user used), `adams-session-<session_id>`, `adams-smallstop-<session_id>` and `adams-numstop-<session_id>`.

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

## Page checks

- The eleven page checks (`PLACEHOLDER COUNT GAP GAP-RHYTHM TABLE SUBLINE THIN A11Y BROKEN COPY COVER RTL`) are described in `modules/line-balance/GUIDE.md`. Detection lives in `modules/line-balance/scripts/page_checks.js` (`inspectPage`, runs inside the page and must stay self-contained); the Tab focus ring, link status and console error parts live in `web_balance.js` (`focusHits`, `brokenLinks`, the console and `pageerror` listeners).
- Cost per page and width: one extra in-page scan, up to 20 Tab presses, and one HEAD request per new same-site link (cached for the run, at most 200). Contrast over images and gradients is not computed; the number of skipped text blocks prints as a WARNING in the verdict.
- `check.py` serves an `.html` file from the nearest parent folder where its first `/root-relative` assets exist (a built `dist/` page is checked with its CSS and links); it prints `HITS: TYPE n, ...` before the verdict.
- A new rule goes into `inspectPage` with a broken fixture that must flag and a correct twin that must stay clean in selftest `web_routes` (the `PC` table).

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
