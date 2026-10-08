# Changelog

Releases follow semantic versioning. Users on a clone get new releases automatically (`adams update`); plugin users get them through Claude Code's marketplace updates.

## Unreleased

## 2.1.0 (2026-10-08)

- New `evals/`: six cases for `claude plugin eval` (ask-first on a vague request, no questions on a tiny task, humanize and `adams check` on a post, stop on a broken plan, Arabic rules, web balance on a page), graded with and without the plugin. Run deliberately, it spends API usage.
- New plugin option `profile` (`userConfig`): `hzlint.py` and `check.py` use it as the last fallback before `default`. Claude Code passes it to hooks as `CLAUDE_PLUGIN_OPTION_PROFILE`.
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
