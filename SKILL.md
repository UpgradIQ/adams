---
name: adams
description: "Invoke automatically on any matching task. Adams, ten modules. Mindset: product-principles (before planning, deciding, designing, auditing, advising). Writing: humanize-writing (text under a person or brand, Arabic and English). Layout QA: line-balance, deliverable-visual-qa (decks, PDFs, docs, images, web pages, dashboards, before delivery). SaaS revamp: UI/UX/CX, ethical conversion, onboarding, pricing, admin. Build: innovation-builder (WordPress blocks), seo-architect (SEO sites), senior-frontend (Next.js, Supabase, Stripe). Workflow: align at start and on drift, diagnose, handoff, retro. Memory: obsidian-vault-memory."
---

# Adams

One skill, ten modules. Read this page, pick the module(s), then load only that module's `GUIDE.md`. Never load all of them.

## Route by task

| The task is | Load | Notes |
|---|---|---|
| Planning, deciding, designing, auditing, scoring a plan, advising, or any product or business judgment | `modules/product-principles/GUIDE.md` | Load first, before any other module. `ALWAYS.md` is its always-on summary. |
| **Start of any non-trivial task (automatic)**, drift while building, stress-testing a plan ("challenge this", "poke holes"), diagnose something broken, failing or slow, write a session handoff, or run a retro on a bad session | `modules/workflow/GUIDE.md` | Adapted from skills.sh (mattpocock/skills). Load `product-principles` first for the judgment calls. Diagnose, handoff and retro live in `references/diagnose.md`, `handoff.md`, `retro.md`; load only the one needed. |
| Any text written for or published under a person or brand (LinkedIn post, reply, DM, email, script, caption, metadata, playbook), Arabic or English | `modules/humanize-writing/GUIDE.md` | Contains the language rules and the `hzlint.py` lint. Mandatory before delivery. LinkedIn post shape: `references/linkedin-post.md`; English tells: `references/english-tells.md`. |
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

## Standing rules every module shares

- Language: code, commits, docs, plans, reports and UI copy are English; chat follows the user's language; content requested in Arabic (posts, scripts, AR metadata) follows humanize-writing section 1. Arabic and English get full word lists, other languages get the structural checks plus a "not covered" notice (`hzlint.py` prints it). Never claim a pass for something a check could not measure.
- Layout: one set of values for every project, in the canonical table of `modules/line-balance/GUIDE.md`. Fix by rewording, never by shrinking the font.
- Scratch output (renders, lint output) goes in the scratchpad, never in the user's own folders.

## Auto-run

`adams check FILE_OR_URL ...` picks the checks by file type (exit 1 if flagged, last line `ADAMS CHECK: CLEAN` or `FLAGGED`); the input-to-checks table is in `docs/COMPANIONS.md`. Scope is the files changed in this task.

- Pick the cheapest check that fits. Do not run a check that cannot apply (pure chat, no layout) and do not re-run a file that has not changed since it last passed.
- Fresh eyes: for Arabic text, published posts and scripts, also spawn a separate reviewer agent with the text alone and the prompt in `modules/humanize-writing/fresh-eyes-prompt.md` (`check.py` prints this reminder after any text check). If no agent is available, say so in the report.
- Dependencies are pre-approved for this skill: scripts install what they need (Playwright and Chromium, `pdfplumber`, `pillow`) on first run. Do not ask first. This overrides the cost and dependency gate for Adams tooling only. If an install fails (no network, locked machine), say so plainly and do not work around it.

Companion skills and pipelines: `docs/COMPANIONS.md`, load only when the task needs them.
Install, profiles, hooks and maintenance: docs/OPERATIONS.md, `adams where` prints the folder.
