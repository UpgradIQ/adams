---
name: adams-extras
description: "Invoke on a matching task. Adams extras, three optional modules. innovation-builder: a canvas, worksheet, framework, matrix, scorecard or planner as a WordPress HTML block. seo-architect: keyword opportunities, a programmatic static SEO site, an internal linking plan, content briefs, and AI search readiness (GEO/AEO: llms.txt, AI crawlers, schema, citable pages). obsidian-vault-memory: save to, search or read the Obsidian vault, remember this, second brain."
---

# Adams extras

Three optional modules that live outside the core Adams plugin. Read this page, pick the module, then load only that module's `GUIDE.md`. The core `adams` plugin supplies the always-on rules, the hooks and `adams check`; a deliverable from these modules still goes through them.

## Route by task

| The task is | Load | Notes |
|---|---|---|
| Canvas, worksheet, framework, matrix, scorecard, planner as a WordPress HTML block | `modules/innovation-builder/GUIDE.md` | `references/` holds the spec contract and the 230-template catalog. |
| Keyword opportunities, programmatic static SEO site, internal linking plan, content briefs | `modules/seo-architect/GUIDE.md` | Load its `references/` files at the step the guide names. |
| AI search readiness (GEO/AEO): llms.txt, AI crawlers, schema, citable pages | `modules/seo-architect/GUIDE.md` section "AI search (GEO/AEO)" | Run `scripts/ai_search_audit.py URL_OR_FOLDER`; facts in `references/ai-search.md`. |
| Save to, search or read the Obsidian vault, "remember this", "second brain" | `modules/obsidian-vault-memory/GUIDE.md` | `references/endpoints.md` and `setup-guide.md`. |

Relative paths (`references/`, `assets/`, `scripts/`) resolve inside the module's folder. Pipeline: an SEO site goes seo-architect, then the core `senior-frontend` module to build it, then `deliverable-visual-qa` when it is a visual deliverable.
