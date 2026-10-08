# Adams companions and pipelines

Load only when the task needs them. Moved verbatim from `SKILL.md` to keep the router small.

## Companion skills (installed separately, Adams routes to them instead of copying them)

Adams does not duplicate what a good skill already does. For these areas load the named skill after the Adams module that applies, and let Adams' rules win on any conflict.

| Area | Skills | Adams rule that wins |
|---|---|---|
| Visual design and UI polish | `high-end-visual-design`, `frontend-design`, `impeccable`, `ui-ux-pro-max`, `design-review`, `motion-designer` | `line-balance` canonical table, `product-principles` (no dark patterns) |
| Marketing copy, CRO, pricing, SEO audits | `copywriting`, `marketing-psychology`, `programmatic-seo`, `seo-audit`, `ai-seo`, `cold-email`, `linkedin-writer` | `humanize-writing` lint and `product-principles` (truth over wishes) |
| Frontend and database craft | `nextjs-best-practices`, `react-best-practices`, `shadcn`, `supabase-postgres-best-practices`, `web-perf` | `senior-frontend` standards |
| Charts and KPI dashboards | `kpi-dashboard-design`, `dataviz` | `line-balance` for any text in them |
| Planning, TDD, verification | `brainstorming`, `writing-plans`, `tdd`, `verification-quality` | `workflow` section 3 |
| Debugging and incidents | `investigate`, `retro` | `workflow` `references/diagnose.md` and `references/retro.md` |

**Missing a capability?** Run `find-skills` (it searches skills.sh) before building one. Installing a third-party skill is a download from outside: name the skill, its source and size to the user and ask first, and read its audit results on skills.sh and its files before you propose it.

## Pipelines (the modules chain, run them in this order)

```
text only      write --> humanize-writing --> deliver
laid-out file  write --> humanize-writing --> build --> line-balance --> deliverable-visual-qa --> deliver
course lesson  (a private add-on skill builds it) --> humanize-writing --> line-balance --> deliverable-visual-qa --> deliver
SEO site       seo-architect --> senior-frontend (build) --> deliverable-visual-qa (if a visual deliverable)
```

## Auto-run: input to checks

| Input | What it runs automatically |
|---|---|
| `.txt` / `.md` | `hzlint` (mode from the file name and headings) plus `arlint` when the text has Arabic |
| `.pdf` | `line_balance` and `title_check` |
| `.pptx` | `textlint` over slide text and speaker notes, then rendered to PDF with LibreOffice and checked like a PDF |
| `.docx` | rendered to PDF with LibreOffice, then checked like a PDF |
| `.html` | serves it on a temporary local port, then `web_balance` at 375, 768, 1440 |
| `http(s)://` URL (site, dashboard, academy) | `web_balance --crawl --max 10`; pass other flags after `--` |
