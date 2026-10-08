# Adams pipelines and auto-run checks

Load only when the task needs them. Kept out of `SKILL.md` to keep the router small.

## Pipelines (the modules chain, run them in this order)

```
text only      write --> humanize-writing --> deliver
laid-out file  write --> humanize-writing --> build --> line-balance --> deliverable-visual-qa --> deliver
course lesson  (a private add-on skill builds it) --> humanize-writing --> line-balance --> deliverable-visual-qa --> deliver
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
