# Changelog

Releases follow semantic versioning. Users on a clone get new releases automatically (`adams update`); plugin users get them through Claude Code's marketplace updates.

## Unreleased

- `web_balance.js` now defaults `--min` to 0.3, the web floor in the canonical table of `modules/line-balance/GUIDE.md` (it was 0.5, which flagged web last lines of 30% to 50% that the rule allows). File checks (`line_balance.py`, pptx, pdf, docx) keep 0.5.

## 2.5.0 (2026-10-09)

- Page checks: eleven new web hit types run at every width in `web_balance.js` (rules in the new `modules/line-balance/scripts/page_checks.js`), each with a broken fixture that must flag and a correct twin that must stay clean in selftest. `PLACEHOLDER` (`lorem ipsum`, `TODO`, `FIXME`, `TBD`, `{{ }}`, `undefined`, `NaN`, `null`, `[object Object]`, `${` in visible text), `COUNT` (a heading that states a count above a list with another number of items), `GAP` and `GAP-RHYTHM` (sections closer than 12px, more than two different gaps between sections), `TABLE` (number columns end aligned with tabular figures, text columns start aligned, header on its column, content 16px from the frame), `SUBLINE` (a paragraph shares its heading's start edge and is no wider than a width-limited heading), `THIN` (main content under 55% of a 1280px or wider viewport), `A11Y` (contrast against the nearest opaque background, 44x44 touch targets at 480px and narrower, `img` without `alt`, heading level skips, no visible focus style on Tab), `BROKEN` (same-site links answering 404, images that failed to load, console errors, uncaught page errors; file:// targets must exist), `COPY` (U+2014 and U+2013, exclamation marks in headings, buttons and labels, Title Case headings), `COVER` (a fixed or sticky element covering text or controls at scroll 0, a `role=dialog` without `aria-modal`, an anchor target under a sticky header), `RTL` (unmirrored direction icons, `text-align: left` and `float: left` on RTL text). Hit lines carry the measured numbers.
- `check.py` prints a `HITS: TYPE n, ...` line before the verdict, shows the last 6000 characters of a check instead of 1500, and serves an `.html` file from the nearest parent folder where its `/root-relative` assets exist, so a page inside a built `dist/` is checked with its CSS and links instead of unstyled.
- Agent deviation gates, so an agent cannot reach green by weakening the referee. New `hooks/adams_deviation_gate.py` (`PreToolUse` on `Bash|Edit|Write|MultiEdit|NotebookEdit`, 5 second timeout, registered in `hooks/hooks.json` and `bin/adams`): test tampering (skip and only markers, deleting or emptying a test file, net removal of assertions), silencing errors (`@ts-ignore`, `@ts-nocheck`, bare `@ts-expect-error`, `eslint-disable`, `# type: ignore`, `# noqa`, `//nolint`, new `any`, configs that loosen strictness), gaming checks (CI workflows, thresholds, snapshots, `.adams/config.json`, `scripts/selftest.py` outside the Adams repo; open after a prompt naming ci, workflow, threshold, snapshot or selftest, which the router records as words only), self-disabling (`ADAMS_*=0` in a command, writes to the user's Claude and Adams config, CLAUDE.md and the plugin cache), and scope (`adams decide --scope "glob,glob"`).
- `hooks/block-risky-git.py`: denies `git commit --no-verify` and `-n`, `--force-with-lease` to `main` or `master`, `rm -r` on the repo root or a tracked folder, SQL `DROP` and `TRUNCATE` through a database client, `supabase db reset` and `prisma migrate reset`; the commit gate also denies staged files outside the recorded scope and leftovers in added source lines (`console.log(`, `debugger;`, `print(`, new `TODO`, `FIXME`, `XXX`, mock data in production paths), each with file and line.
- `hooks/adams_stop.py`: blocks once when a `--small` session grows past 3 source files or 80 changed lines, and once when the final message carries figures (percentages, `10x`, `5 ms`, `N tests`, `all tests pass`, `CLEAN`, `score N`) that no command output of the session shows.
- `adams decide` now writes `- YYYY-MM-DD HH:MM:SS: ...` bullets (the time lets the gates tell this session's decisions from older ones) and takes `--scope "glob,glob"`. Link installs made earlier need `adams uninstall` and `adams install` to register the new hook.
- Selftest `deviation_gates` has a denied case and an allowed twin for every gate, including the router word store, the scope session rule, the destructive command list, the leftover allowances, and the figures check with a fake transcript.
- `ORPHAN` counts inline-block chips: an inline-block inside a text block (a code span styled as a chip) is part of its line, so a last line made of a wide chip and a full stop is no longer read as the stub `.`. Selftest has the case (`chip_good.html`).

## 2.4.2 (2026-10-09)

- Web balance catches broken diagrams that passed with only STRESS hits. New hit type `DIAGRAM`: in a container with 3+ absolutely positioned text nodes or a large inline SVG, text boxes, positioned boxes and SVG shapes (including marker arrowheads) closer than 8px, overlapping, or outside the container's box are flagged (a label in its own card, the background ring and shapes of one SVG are exempt). New hit type `MARKER`: in 3+ repeated rows with a small marker or round numeral badge, marker centres must share one x (1px), sit on the first text line's centre (2px), and a connector (pseudo-element of the list or a row, or a thin element) must run through the marker centres and, at list level, start and end on the first and last one. Both count in `FLAGGED`.
- `WRAPPED` root cause fixed: an element with own text and block children (a flex node holding a numeral and a bare label) was never measured, because the text was in no text block; its own text is measured now. A short label in a flex row or an absolutely positioned node was also never treated as short (only tags, lists, buttons and pills were), so a label such as "The person opens one" wrapping to two lines passed or showed as ORPHAN; up to 12 words with no sentence punctuation now count as WRAPPED there. `UNEVEN` also compares sibling diagram nodes (same container and class, absolutely positioned or flex) that differ in line count, even when their tops differ.
- Selftest has an old (must flag) and a fixed (must not flag) fixture for each: arrows touching cards around an SVG ring, dots off a timeline and top aligned, and a wrapping numeral plus label in a flex node and in an absolute node. A full check of the Adams site (`/`, `/adams`, `/adams/install` at 375, 768 and 1440, `--min 0.3`, `--stress`) stays CLEAN.

## 2.4.1 (2026-10-09)

- Shell writes are gated like edits: the align gate (`hooks/adams_align_gate.py`) is now also registered on `PreToolUse` `Bash`. A write-like command (redirect, `tee`, `sed -i`, `perl -pi`, `mv`, `cp`, a script opening a file for writing) that names a source file in a git work tree is denied until `adams decide` runs, with the same allow rules as an edit (docs, `.adams`, `.planning`, the Claude scratchpad, non-git folders). Read-only commands, tests, builds and git commands never trigger it. The router (`hooks/adams_router.py`) runs the same path rules (auth, UI, tests first, prose) on the files a write-like Bash command names, and a shell-written test file counts as a test edit. New helper `bash_targets` in `hooks/adams_gates.py` finds the targets before the command runs. Link installs made earlier keep the old matcher until `adams uninstall` and `adams install` are run again. Shortcut: for non-redirect writes any source path in the command counts, even one it only reads (`cp src/a.js /tmp/x`).
- Stop check sees shell edits: `hooks/adams_verify_record.py` also adds the changed files that a write-like Bash command names (redirect, `tee`, `sed -i`, `perl -pi`, `mv`, a script that writes a file) to the session's touched list, so code changed through the shell and never verified now blocks the stop. Before, such a session had an empty list and was never checked.
- Scorecard fixes after the first run: the checks now count shell writes (`cat >>`, a Python heredoc, `perl -pi`) as edits in any path form, and order an edit and a test run inside one command. Re-scored offline, the first run goes from 93.8 to 100. New `scripts/scorecard.py --rescore DATE` re-runs the checks on saved results without model calls; `--run` keeps each repo under `scorecard/results/<date>-repos/` and records hook events (`--include-hook-events`) in the transcripts.

## 2.4.0 (2026-10-09)

- Stop check scoped to this session: `hooks/adams_verify_record.py` now also runs after `Edit`, `Write`, `MultiEdit` and `NotebookEdit` and appends each file path to `adams-touched-<session_id>` in the temp folder. `hooks/adams_stop.py` checks only the `.md` and `.txt` files and verifies only the source files this session wrote, so a session is never blocked on files another live session edits in the same folder (foreign changes are not reported). Without a session id or a touched list the Stop hook never blocks. The align gate no longer stores a tree snapshot for the Stop check. Link installs made earlier keep the old `Bash` matcher on that hook until `adams uninstall` and `adams install` are run again.
- Optional modules moved out of core into a second plugin, `adams-extras` (`plugins/adams-extras/`, listed in the same marketplace): `innovation-builder`, `seo-architect` (with `ai_search_audit.py`) and `obsidian-vault-memory`, moved with their history. Install with `/plugin install adams-extras@adams`. Core `SKILL.md` drops those rows (description 629 to 532 characters, `adams tokens` SKILL.md 1603 to 1426, typical text task 7597 to 7420) and keeps one pointer line; `scripts/release.py` bumps both manifests; selftest fails if core names a moved module or the two manifests disagree on the version.
- Context router: `hooks/adams_router.py` adds a short guidance block by context with fixed rules (no AI, no network). Triggers: a bug or error prompt or a failed test run (diagnose), "I don't understand" (plain language), an edit to an auth, session, token or secret path (security checklist), an edit that adds a dependency (cost check), a UI file edit (`adams check` at three widths), the first source edit with no test yet (tests first), an edit to published copy (minimum effective edit). Each rule fires once per session, at most two blocks per call, 600 characters each. Registered on `UserPromptSubmit`, `PostToolUse` (`Edit|Write|MultiEdit|Bash`) and `PostToolUseFailure` (`Bash`), 5 second timeout. Opt out with `ADAMS_GATES=0`.
- Commit review gate: the first `git commit` of a session that stages source is denied once with a review request (correct, safe, holds under load, tested, fast, lean); the retry passes. Opt out with `ADAMS_REVIEW=0`.
- Feature test gate: a commit message starting with `feat`, `add ` or `implement ` that stages source must also stage a test file, like the `fix` rule.
- Selftest covers each router rule, once per session, silence, opt-out, garbage input, the review gate and the feature test gate.
- Stress mode: `web_balance.js --stress` mutates a copy of the live DOM (twice the words, a 40 character unbroken token, 9-digit numbers, blanked lists), reloads between passes, and reports layout breakage only as hit type `STRESS` with the mutation kind and a reason (page overflow, child past its parent, text past its own box, clipped text, overlapping sibling text). Breakage that exists before any mutation is reported once as kind `as-is`. Stress runs at widths 375 and 1440, at most 30 elements per pass, and is skipped above 20 pages unless `--stress-all`. `adams check` passes `--stress` for `.html` files and URLs; `-- --no-stress` skips it. Selftest has a nowrap chip that must flag and a wrapping page that must not.
- Real-task scorecard: `adams scorecard` and `scripts/scorecard.py` with 8 programming tasks under `scorecard/tasks/` (asks before building, bugfix with a regression test, tests first, no scope creep, secret guard, verify before done, layout overflow under stress, dependency restraint). Each has a fixture project, a prompt and a hidden deterministic check. `--dry-run` (part of selftest, no model calls) proves each check fails on the untouched fixture and passes on its golden solution; `--run [--tasks] [--runs] [--max-cost]` runs `claude -p` with the user's real configuration, prints a table and a score out of 100, and writes `scorecard/results/<date>.json` (git-ignored). A run costs about $0.15 to $0.70 per case.

## 2.3.1 (2026-10-09)

- Adams stands alone: no content file names another skill, plugin or third-party project. The routing table to outside skills and the paragraph about installing them are removed, that doc is now `docs/PIPELINES.md`, and third-party license notices live only in `NOTICE`. `adams selftest` fails if a tracked file other than `NOTICE` names one.

## 2.3.0 (2026-10-09)

- Hard gates as hooks, so the rules hold when the prompt is ignored. Align gate: the first code edit of a session is denied until `adams decide` records the decisions (or `adams decide --small` the one assumption). Verify gate: test, build, typecheck and lint runs are recorded with a working tree fingerprint, and the Stop hook blocks once when code changed since the last green run. Commit gate: `git commit` is denied for a staged secret or `.env` file, a `fix` commit without a test, and source changed since the last green run.
- New `adams decide [--small] TEXT` command appends a dated bullet to `.adams/decisions.md`. New shared helper `hooks/adams_gates.py`.
- Opt-outs: `ADAMS_GATES=0` (all gates), `ADAMS_VERIFY=0` (verification only). Every deny message ends with its override.
- The git guardrail hook timeout is 20 seconds (was 5) because the commit gate reads the staged diff.
- `ALWAYS.md` no longer says to ask only for money and irreversible actions: open decisions, taste and access are asked first.
- Selftest runs each gate as a hook against a temp git repo.

## 2.2.2 (2026-10-08)

- Web balance classifies short text by rendered role, not class name. The `[class*=badge|chip|pill|tag]` match is gone (a `stagecard` holding a paragraph was flagged WRAPPED, and agents renamed classes to hide it). Short means a short-text tag, a list, button, label, table header, nav or tab role, or a chip by rendering (inline-block, inline-flex, inline-grid, or a painted pill) with 6 words or fewer. A paragraph is never short.
- New hit type `SHRUNK`: an element whose inline `font-size` a script changed after load. Scripts that shrink type until copy fits one line hid too-long copy and broke one type scale. It counts in FLAGGED like the other types.
- Guidance: renaming a class or selector to dodge a check is a defect, and wrapping is fixed by shorter copy or a deliberate responsive type step in CSS (line-balance guide, visual QA guide).
- Selftest covers a paragraph in a `stagecard`, a non-chip-named inline-block pill, and a page that shrinks type.

## 2.2.1 (2026-10-08)

- Web balance scans every view of a hash-routed page. Routes (`#/x`, `#!/x`, `[data-route]` values) were stripped to one URL, so a 47-view single-page app was checked as one page and reported CLEAN. Views of one document now share one page per width and switch with the hash, instead of a new browser context per route.
- The check verdict states its coverage: `ADAMS CHECK: CLEAN (2 files, 3 pages x 3 widths)`. `web_balance.js` prints `PAGES n WIDTHS ... ROUTES n`, and a `WARNING` line when in-page routes were not scanned or the crawl stopped at `--max`. `check.py` prints each warning before the verdict and repeats it inside the parentheses. Warnings never change the exit code.
- The same defect on many views (a shared drawer or footer) prints once, then `also on N more routes`. `FLAGGED` counts unique defects and `ROUTE-HITS` the raw count; the `--out` JSON keeps every hit.
- Guidance: a page with in-page views is CLEAN only when every view was scanned, and delegated agents quote the page count, never only the verdict (line-balance guide, visual QA guide, `ALWAYS.md`).
- Selftest builds a two-route page with a defect on one route and checks the crawl, the plain anchor case and the verdict coverage.

## 2.2.0 (2026-10-08)

- Progressive disclosure: `modules/workflow/GUIDE.md` keeps align, verify and complete output, and diagnose, handoff and retro moved verbatim to `references/diagnose.md`, `handoff.md` and `retro.md`. `modules/humanize-writing/GUIDE.md` keeps sections 1 to 5, and the LinkedIn post method and the English tells moved verbatim to `references/linkedin-post.md` and `references/english-tells.md`. Each guide ends with a router line. Workflow guide 1388 est tokens (was 2172), humanize guide 2695 (was 4650), typical text task 7640 (was 10324). Selftest caps the two guides at 1530 and 3000 est tokens and checks the new reference files exist.
- Token cost: the reminder hook prints once per session (about 450 characters, was 790 on every prompt), `ALWAYS.md` is about 25% smaller with every rule kept, and `SKILL.md` is 44 lines (was 84) with the pipelines and the input-to-checks table moved verbatim to `docs/PIPELINES.md`.
- `adams tokens` prints the estimated token cost (chars/4) of every always-on file, `SKILL.md` and each module. Selftest caps the reminder at 450 characters, `SKILL.md` at 65 lines and 1750 est tokens, `ALWAYS.md` at 950 est tokens.

## 2.1.2 (2026-10-08)

- Evals: `stop-gate` checks that flagged text triggers a check before the agent finishes (with Adams 1.00, without 0.25); `plan-breaks` and `tiny-typo-fix` are tagged `regression-guard` because they pass either way on purpose.
- The workflow guide no longer points at a setting that Adams does not own.
- The skill description is 629 characters (was 883) and `SKILL.md` is 84 lines (was 138), cutting the always-on and on-invoke token cost without touching the routing table.
- Install, profiles, hooks, maintenance and the repo layout moved verbatim to `docs/OPERATIONS.md`, with one pointer line left in the router.
- Selftest caps `SKILL.md` at 105 lines (was 160).

## 2.1.1 (2026-10-08)

- Web balance now checks pages whose content sits under `display: contents` wrappers or fades in on scroll (reduced motion is forced), splits grid rows by vertical overlap, and ignores screen-reader-only table headers.
- `adams uninstall` removes hook events it emptied instead of leaving empty lists.
- README lists what runs automatically.
- `adams install --link` links the skill and registers the hooks even when the plugin is enabled, for apps that do not load marketplace plugins.
- Evals: graders now score the delivered work (deterministic checks where possible), turn budgets fit Adams' reviewer passes, and the drift case tests scope growth. Measured with and without the plugin: auto-ask, `adams check` use and humanize rules show a clear gain; the drift and typo cases pass either way (they guard against regressions).

## 2.1.0 (2026-10-08)

- `evals/` holds six cases for `claude plugin eval` (ask-first on a vague request, no questions on a tiny task, humanize and `adams check` on a post, stop on a broken plan, Arabic rules, web balance on a page), graded with and without the plugin. Run deliberately, it spends API usage.
- Plugin option `profile` (`userConfig`): `hzlint.py` and `check.py` use it as the last fallback before `default`. Claude Code passes it to hooks as `CLAUDE_PLUGIN_OPTION_PROFILE`.
- New AI-search audit: `modules/seo-architect/scripts/ai_search_audit.py URL_OR_FOLDER` (llms.txt, AI-bot rules in robots.txt, sitemap, titles, descriptions, canonicals, JSON-LD, brand spelling), a section in the seo-architect guide, `references/ai-search.md`, and a router row.
- New humanize regression corpus (`modules/humanize-writing/tests/corpus/`, English and Arabic, stock-AI and plain samples) checked by the selftest.
- README: "Scheduled audits" with a copy-paste prompt for `/schedule` and `loop`.
- New Stop hook (`hooks/adams_stop.py`): checks the `.md` and `.txt` files changed in the working repo when the agent finishes, and sends it back to fix BLOCK hits. Files that passed are not re-checked until they change.
- New SessionStart hook (`hooks/adams_context.py`): reloads `.adams/decisions.md` (settled decisions) after a start, restart or compaction. The workflow guide records decisions there.
- Budget guards in the selftest: reminder at most 900 characters, `SKILL.md` at most 160 lines, and no network imports in the hooks (telemetry-free). `SECURITY.md` states it.
- New: Adams asks on its own. At the start of any non-trivial task, and again whenever the work drifts, it reads the project docs, then asks the open decisions in one round (max 4), each with a recommended best practice and the reason, records the answers, and checks the work against them at checkpoints. No "ask me" needed. Loop in `modules/workflow/GUIDE.md` section 1; wired into `ALWAYS.md`, the router and the prompt reminder.
- `main` and the release tags are protected: no force pushes or deletions, and release tags can no longer be moved, so an update always gets the code that was released.

## 2.0.2 (2026-10-07)

- The reminder and `ALWAYS.md` name the plugin form of the skill (`adams:adams`), and use neutral wording for the owner.
- `adams doctor` prints the installed version; the README explains how to verify a plugin install.

## 2.0.1 (2026-10-07)

- Plugin installs and clone installs no longer double up: with the plugin enabled, `adams install` skips the skill link and the hooks, and `adams doctor` counts the plugin as the source of both.
- Release tags are annotated, so `git push --follow-tags` publishes them.

## 2.0.0 (2026-10-07)

- **Coming from 0.1.0?** That release had no updater, so run `git -C <your clone> pull` once (or `claude plugin marketplace update adams` for the plugin). From 2.0 on, updates are automatic.
- **Updates that reach you by themselves.** `adams update` moves a clone to the newest release tag, and a new SessionStart hook checks once a day and updates a clean clone quietly (opt out with `ADAMS_AUTO_UPDATE=0`). Plugin users enable auto-update in `/plugin` or in settings (see the README).
- **Versioned releases.** One `VERSION` file, this changelog, and a release workflow that publishes a GitHub Release when a `vX.Y.Z` tag is pushed. `scripts/release.py` cuts a release.
- **Checks on what you changed.** `adams check --changed` and `--since REF` skip untouched files, for pull requests and CI.
- **One profile per project.** `adams init` writes `.adams/config.json` so everyone shares the same rules.
- **Visible versions.** A release badge on the repository page, `adams version`, and an Updates section in the README.
- Fixed: HTML tag lines no longer count as repeated openers, and a file named README is no longer treated as a direct message.

## 0.1.0 (2026-10-07)

- First public release: the Adams skill with ten modules, profiles (`default`, `strict-ar`), the `adams` CLI, hooks, plugin manifests and CI.
