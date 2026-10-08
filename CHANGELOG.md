# Changelog

Releases follow semantic versioning. Users on a clone get new releases automatically (`adams update`); plugin users get them through Claude Code's marketplace updates.

## Unreleased

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
- Token cost: the reminder hook prints once per session (about 450 characters, was 790 on every prompt), `ALWAYS.md` is about 25% smaller with every rule kept, and `SKILL.md` is 44 lines (was 84) with the companion skills table, the pipelines and the input-to-checks table moved verbatim to `docs/COMPANIONS.md`.
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
