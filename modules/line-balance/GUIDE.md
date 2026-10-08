# Line balance

The owner treats unbalanced text as a defect, not polish. This module runs on **every writing task whose output has a fixed layout**: .pptx, Slides, .docx, PDF, posters and images with text, HTML pages, whole websites, SaaS dashboards and academies. It runs after the content is written and before delivery, together with the humanize-writing lint. It does not apply to plain chat replies, since they have no fixed width.

## The rules

1. **No orphan word.** No paragraph, bullet, card body, caption, table cell or subtitle ends with one word alone on its last line.
2. **Last line at least 30% on web, 50% in files (pdf, pptx, docx)** of the paragraph's widest line. See the canonical values table below.
3. **Short items stay on one line.** Bullets, buttons, labels, chips, nav links, tabs, stat captions, table headers and h2 to h6 never wrap. A two-word label never splits. An h1 or hero heading may take 2 lines, never more.
4. **Symmetry across siblings.** Cards, columns or list items that sit side by side in one row have the same number of lines.
5. **No dead words** (definition below).
6. **Fix by rewording**: add or trim words, or rebalance the sentence. Never fix by shrinking the font, squeezing letter spacing, forcing `white-space: nowrap`, inserting `<br>` or manual line breaks, or hiding text. Widening a box is allowed only inside the existing grid, so the layout stays symmetric. For HTML rendered to PDF, set `text-wrap: pretty` on paragraphs and list items and `text-wrap: balance` on table cells and headings, then still run the check. Known false positives of the file checker: separate stacked labels, code lines, step counters, a URL on its own line on purpose, and Arabic words split at a diacritic by pdftotext; look at every hit on the rendered page.
7. Every language follows the same rules. The checkers measure geometry only, so they work in both text directions and in any script that puts spaces between words (Latin, Arabic, Cyrillic, Greek, Hebrew, Devanagari). Scripts written without spaces (Chinese, Japanese, Thai) cannot be checked for orphan words: say so in the report instead of claiming a pass.

### Dead words

A dead word is any word or phrase you can delete without changing the meaning, the tone or the facts. Delete or replace it while you rebalance lines.

- Intensifiers and hedges: very, really, just, actually, basically, simply, truly, quite, totally, literally, جداً when used as filler, فعلاً، حقيقي، ببساطة.
- Padding phrases: "in order to" (use "to"), "the fact that", "it is important to note", "at the end of the day", "في الحقيقة"، "في النهاية"، "بمعنى آخر".
- Doubles: two words with the same meaning side by side ("each and every", "سهل وبسيط").
- Empty UI copy: "Click here", "Learn more" with no object, "Welcome to our platform", labels that repeat the heading above them.
- The banned lists in humanize-writing (`hzlint.py`) count as dead words too, so run it on the copy.

Never delete a product name, a number, a legal or pricing term, or a word a user needs to complete a task.

## Canonical values (conflict table)

One set of values for every project and every prompt. An older prompt, spec or note that says otherwise is superseded by this table (the owner's Notion prompts disagreed with each other on width, heading length, card lines, `<br>` and more).

| Topic | Canonical value |
|---|---|
| Content width | From the project's `DESIGN.md` (never a number from an old prompt: 1230, 1240, 1400 and 1600 all appear in old prompts). Dashboards follow the same width unless `DESIGN.md` says full-width. |
| How balance is measured | By rendered lines in the real font, never by character count and never by element height |
| Measure at | 375 and 1280. For checks also 768 and 1440 |
| Card body | 2 lines (a 3rd line is trimmed by rewording) |
| Table insets | First and last cell content at least 16px from the visible edge of the box holding the table; text column takes the spare width, number columns hug their content (owner, 6 Oct 2026) |
| Decorative shapes and frames | Shapes are whole, closed and fully inside their section (never cropped by an edge, a diagonal clip-path or a skewed band); at most two framed levels, never box > box > box (owner, 7 Oct 2026) |
| Item count in a grid | Fills every row evenly at 375, 768 and 1280: 3 columns take 3, 6 or 9; 2 columns take 2, 4 or 6; never 5 or 7, never a lone item in the last row (owner, 6 Oct 2026) |
| Last line of a paragraph | At least 30% on web, at least 50% in files (pdf, pptx, docx) |
| Short text | Titles, labels, chips, buttons, nav items, bullets, stat captions: one line, never wrap |
| Heading length | Hero heading 2 lines max, other headings 1 line. No fixed word count or width percentage |
| How to fix | By rewording only. Never `<br>`, `nowrap`, `overflow:hidden` or a smaller font, and never a script that shrinks text to fit (fit-text JS). A per-breakpoint size set once in the type scale (a mobile token) is design, not a fix, and is allowed. Only exception: a fixed-stage Keynote-style course landing page, which may fix its stage |
| Em dash and en dash | Never. Use `·`, colon, comma or rewrite. A plain hyphen only for ranges |
| Case and digits | Sentence case for UI copy. Latin digits |
| Colour and spacing | Tokens only, no inline hex |
| Accessibility | WCAG 2.2 AA minimum |
| Deploy and push | Each project's own `AGENTS.md` decides. Destructive database changes always need the owner's confirmation |
| Numeric rules | These are not "guidelines"; a hit is a defect until it is reworded or the exception is listed in the report |
| Dashboard type size (member and admin) | Body 15px, secondary 14px, nothing below 13px; headings 17 / 20 / 28px; size tokens only, never literal sizes (owner, 6 Oct 2026: members complained text was too small) |

Tool note: `web_balance.js` defaults to `--widths 375,768,1440` and `--min 0.5`. For web work pass `--widths 375,768,1280,1440` and, when the project's rule is 30%, `--min 0.3`. Files keep the 0.5 default of `line_balance.py`.

## Which checker to use

| Output | Checker | Command |
|---|---|---|
| pptx, docx, PDF, image exported to PDF | `scripts/line_balance.py` | `python3 line_balance.py file.pdf [--min 0.5] [--pages 3-7]` |
| Generated deck, before rendering (optional, faster) | `scripts/wrap_sim.py` | `python3 wrap_sim.py textlog.json 0.5` |
| Website, web app, dashboard, academy, any HTML | `scripts/web_balance.js` | see "Websites and apps" |

`deliverable-visual-qa/scripts/lines.py` now forwards to `line_balance.py`, so both modules always give the same result.

All three print `FLAGGED n` and exit with 1 when n is above 0.

## Files (pptx, docx, PDF)

1. Write the content, then build the file.
2. Render to PDF. For pptx or docx use `python <pptx skill>/scripts/office/soffice.py --headless --convert-to pdf file.pptx`, because bare `soffice` can hang.
3. Run `line_balance.py` on the PDF and keep its output in the scratchpad, never in the user's own folders.
4. Fix every hit at the source (the generator script or the document), then rebuild, re-render and re-run until you get `FLAGGED 0`.
5. Render every page as an image and look at it. The checker covers lines only. The visual pass covers overlap, overflow and spacing.

For generated decks you can also log every text box (`slide`, `text`, `w` in inches, `fs`, `bold`, `cs`) to JSON while building, then run `wrap_sim.py` to find problems before rendering. The PDF check is still the final proof.

## Websites and apps (public site, User dashboard, Admin dashboard, academy)

`web_balance.js` opens every page in a real browser, measures each word's position, and checks each text block at every screen width.

### Setup

Nothing to install by hand. Every script installs what it needs on its first run, then reuses it:

- `web_balance.js` installs Playwright and Chromium once into `~/.cache/adams-line-balance`. It sits outside every project, so no `package.json` changes. That is about 10 MB for the package and about 150 MB for Chromium, shared by all projects. If the project already has Playwright, the script uses that copy.
- `line_balance.py` installs `pdfplumber`, and `wrap_sim.py` installs `pillow`, with pip (into the active venv if there is one, otherwise `--user`).
- Each script needs Node or Python itself, plus internet access on the first run. If an install fails (no network, or a locked-down machine), the script stops with the error. Report that to the owner instead of working around it.

Save session files to a git-ignored folder such as `.lb/` and add `.lb/` to `.gitignore`.

Renaming a class, id or selector to dodge a check is a defect, never a fix. The checks read rendered content and role, not names.

Fix wrapping by shortening the copy or by a deliberate responsive type step in CSS, never by a script that shrinks type to fit. SHRUNK hits are defects.

### Sign in to protected areas

Make one test account per role. Never use a real customer account, and never print or commit the passwords.

```
LB_EMAIL=user@test LB_PASSWORD=*** node web_balance.js login --url https://site/login --out .lb/user.json
LB_EMAIL=admin@test LB_PASSWORD=*** node web_balance.js login --url https://site/login --out .lb/admin.json
```

If the login form is unusual, set `LB_EMAIL_SEL`, `LB_PASS_SEL` and `LB_SUBMIT_SEL` to its CSS selectors. If login uses a magic link or 2FA, ask the owner for a session file. Do not try to bypass it.

### List the pages

Choose one of these:

- **Crawl** with `--crawl`. It follows same-site links, up to `--max` pages (300 by default), and skips logout links and files. Use `--start-user /dashboard` and `--start-admin /admin` so each role crawls its own area.
- **URL list** (`--urls pages.txt`), which is better for apps where many pages are not linked:

```
# public
/
/pricing
/ar/pricing
# states: open a modal, a tab or an empty state before checking
/academy/course/1 | click:[data-test=syllabus-tab] | wait:400
@user /dashboard
@user /dashboard/billing | click:[data-test=upgrade] | wait:500
@admin /admin/users
```

Generate the list from the router (Next.js `app/` folders, a sitemap, or the admin menu) so no page is missed. Cover the empty state and the filled state of dashboards, open modals and drawers, and both Arabic and English routes.

### Run

```
node web_balance.js --base https://staging.site --urls pages.txt \
  --auth user=.lb/user.json --auth admin=.lb/admin.json \
  --widths 375,768,1440 --out .lb/report.json
```

Each hit reports its type (`ORPHAN`, `WRAPPED`, `HERO`, `UNEVEN`, `GRID`, `EDGE`, `CROP`, `NEST`, `SLANT`, `ERROR`), the width, the role, the URL, a CSS selector and the text. Any `ERROR` means a page did not load or a step selector failed. Fix the list and run again, because an unchecked page is not a pass.

A single-page app or any page with in-page views is CLEAN only when every view was scanned (crawl or `--urls`). The report states the pages and widths covered. Delegated agents quote the page count, never only the verdict. Hash routes (`#/x`, `#!/x`, `[data-route]`) count as pages: the crawl loads the document once per width and switches views. The summary prints `PAGES n WIDTHS ... ROUTES n`, `FLAGGED` counts unique defects, `ROUTE-HITS` the raw count (the same defect on 40 views prints once, then `also on 39 more routes`; `--out` keeps every hit), and a `WARNING` line appears when in-page routes were not scanned or the crawl stopped at `--max`. `check.py` copies the page and width count into its verdict, for example `ADAMS CHECK: CLEAN (1 page x 3 widths)`.

Run it on local dev or staging, never against production with an admin account that can change data. The checker only reads, but the `click:` steps in your list press real buttons.

### Fix

1. Find the string in the code. Search the repo for the text, or for its i18n key in the translation files.
2. Reword it so the line balances at **all three widths**. A fix for 1440px that breaks 375px is not a fix.
3. Text that comes from the database or a CMS (course titles, admin-entered content) is fixed in the data, or by a length rule in the form that creates it. List these hits for the owner rather than editing production data yourself.
4. Mark an element with `data-lb-ignore` only for text that must stay as is (code, a legal clause, a user's own name), and list every ignore in the report.
5. Re-run until you get `FLAGGED 0`, then take screenshots of the key pages at 375px and 1440px and look at them.

### Large sites

Follow the pilot rule. Fix one page end to end, show the before and after, and wait for his approval before rolling out to every page.

## Report to the owner

- The checker and the command used, the page count, the widths and the roles covered.
- Hits before and after, for example `ORPHAN 41 -> 0, WRAPPED 12 -> 0, UNEVEN 5 -> 0`.
- Every accepted or ignored hit, with the reason.
- What was not covered: pages behind 2FA, states you could not open, CMS content left for the owner.

## Known limits

- **Files:** the PDF check is only trustworthy with fonts LibreOffice has in metric-compatible form (Arial, Calibri, Cambria, Times New Roman, or any font installed in the sandbox). With other fonts, say so in the report. Row symmetry needs at least three sibling blocks with the same top edge and font size, so check two-column layouts by eye.
- **Web:** the browser checker uses the real fonts, so it is exact for the widths tested. Text revealed by hover, or by animation after load, is only checked if a `wait:` or `click:` step brings it on screen. Canvas and SVG text is not checked.
