# Settled decisions (2026-10-09)

- Hard gates are hooks (deterministic), not prompts: align gate, verify gate, commit gate.
- Code engineering comes first; the plugin must be strong on verified code before more writing or design modules.
- A real-task scorecard is run per release (later phase, not part of the gates task).
- Adams never names other skills, plugins or third-party projects; third-party license notices live only in NOTICE. Selftest enforces it.
- Modules without tests are pruned into separate optional plugins (later phase).
- 2026-10-09: pruning done: innovation-builder, seo-architect (with ai_search_audit.py) and obsidian-vault-memory moved to the optional plugin adams-extras (plugins/adams-extras, same marketplace). Core keeps one pointer line in SKILL.md; the Stop check now looks only at files the session itself wrote.
