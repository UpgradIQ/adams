# Deliverable Visual QA

Run before sending or saving any visual or course deliverable. A file that fails a blocking check is fixed, re-rendered and re-checked. Never call a file done without proof of the check.

## Severity

- Blocking: a slide title or subtitle on more than one line, a broken line (a single word alone on the last line of any paragraph, card, label, cell or caption), truncated or overflowing text, overlap, bad wrapping, misalignment, a bullet or marker not level with its text, a script PDF whose pages do not match the deck slides one to one, Arabic that addresses one gender in the singular, a literal translation or an expression that makes no sense in context, empty slide, broken icon or substituted font, incomplete RTL, broken arrow, contrast below 4.5:1, banned word or AI filler, a humanize-writing lint BLOCK hit or an open fresh-eyes AI-pattern finding, count-promising title, wrong or inconsistent number, unlabeled illustrative data, old brand name, AR/EN mismatch, missing required file.
- Fix before delivery if at all possible, otherwise report: cramped layout, inconsistent terminology, awkward phrasing.

## 1. Render and look

```bash
pdftoppm -r 40 -png file.pdf pg && montage pg-*.png -tile 6x -geometry +4+4 -background '#777' sheet.png
pdftoppm -r 100 -png -f N -l N file.pdf detail
```

- PPTX: use the matching PDF export (or convert with LibreOffice) and render it.
- HTML: print to PDF with Playwright/Chromium, then render.
- Read the images yourself. Extracted text alone never counts as a visual check.

## 2. Measured title and subtitle line check (blocking)

Every slide title and every subtitle must sit on exactly one line. Measure it from the rendered PDF with pdftotext -bbox-layout, never estimate. Any title or subtitle on more than one line blocks delivery.

Code: `scripts/title_check.py` in this module (run it from there, do not paste it).

- The title is the block with the tallest line; the subtitle is the first block below it. Exit code 1 means delivery is blocked.
- If a slide has no subtitle, confirm the block it picked is body text, not a missed subtitle, by looking at the rendered page.
- Title rule: one line at the real size (the measurement above decides, never a character count), a natural, grammatical sentence with no counts.
- Subtitle rule: one line, on its own line under the title; longer explanations move to the speaker notes or the playbook.
- Short labels (pills, dividers, kickers) fit one line, about four words maximum.
- Fix length by rewriting (line-balance rule 6).

## 2b. Broken-line check (blocking, every file, every language)

The rule is line-balance rules 1 to 3 (no orphan word, last-line minimums, short items on one line), in English, Arabic or any language. This section only runs it on the rendered file.

Code: `scripts/lines.py` in this module, which forwards to `line-balance/scripts/line_balance.py`, the single checker for files (run it from there, do not paste it). For websites and dashboards use `line-balance/scripts/web_balance.js`.

- Run it on every rendered PDF. It handles Arabic and English the same way, and the old `rtl` flag is accepted but no longer needed.
- Look at every hit on the rendered page. Known false positives: separate stacked labels, code lines, step counters, a URL placed on its own line on purpose, and Arabic words split at a diacritic by pdftotext. Everything else is fixed.
- Chat drafts and Markdown files for other apps: read the rendered preview where one exists and avoid one-word closing lines in short captions and labels.

## 3. Layout checklist

- No cut-off, overflowing, overlapping or footer-colliding text; no awkward wrapping or misaligned elements.
- Sibling cards and columns carry equal weight: same line count, similar length, same grammatical form. Never truncate a phrase to fit; shorten the idea or split the slide.
- No empty slides.
- No tofu boxes or missing icons (private-use glyphs U+F000 to U+F8FF need their icon font; prefer vector icons); no substituted fonts.
- Arabic uses a real Arabic font (for example IBM Plex Sans Arabic); never a monospace or Latin fallback for Arabic labels.
- Readable size on a phone.
- Bullets, dots, ✗/✓ marks, step numbers and icons sit level with the first line of the text beside them. Render list slides and pages at 150 dpi, crop the list and look. PowerPoint and LibreOffice add line leading above the first line, so markers placed at the top of the text box sit too high; move them to the first line's optical center.

## 4. Full RTL for Arabic versions

- dir=rtl; text, lists and tables start on the right.
- Column order, card order, timelines, process flows, charts and directional icons mirrored.
- Mixed Arabic/English lines read in the correct order.
- In SVG keep the root LTR, place elements mirrored, and put direction="rtl" on each Arabic text element.
- The eye moves right to left on every page.

## 5. Arrows and connectors

- Start at the source element's edge, never inside it.
- Tip exactly on the target edge: not inside, not short.
- Correct direction; clean route crossing nothing, inside the canvas; mirrored in Arabic.
- SVG marker whose tip lands on the endpoint:

```html
<marker id="a" markerUnits="userSpaceOnUse" markerWidth="9" markerHeight="9" refX="9" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z"/></marker>
```

- Prefer orthogonal paths with rounded corners for loops. Inspect every arrow at 100 dpi or more.

## 6. Contrast (WCAG AA)

Every text/background pair must reach 4.5:1 (3:1 only for large bold headings). Approved tokens: success #05804D on light backgrounds, error_dark #FF6B6B for red text on dark panels.

Code: `scripts/contrast.py` in this module (run it from there, do not paste it).

Muted grays in footers and captions are the usual failures.

## 7. Text lint

Run on metadata, scripts, documents and pptx text, then read every hit in context:

Code: `scripts/textlint.py` in this module (run it from there, do not paste it).

False positives: a banned string inside a longer legitimate word (والمقال, سيولّد, سيوفر, المؤسسيون) is reworded to break the substring, never ignored and never fixed by deleting real content. AI filler words are replaced with plain wording.

Also read every title and subtitle aloud: it must be a natural, grammatical sentence a native speaker would say.

## 7b. Arabic language check (blocking)

Run on the recording script, speaker notes, the Arabic playbook, metadata-AR and any Arabic text, then read every hit in context. The only copy is `scripts/arlint.py`; run `python3 arlint.py FILES...`. Its code is in the script below.

Code: `scripts/arlint.py` in this module (run it from there, do not paste it).

- Matching is whole-word, with an attached و / ف / ب prefix allowed, so "عندكم" or "موقعكم" never trigger "عندك" or "موقعك", while "ونشحن" is still caught. Exit code 1 means there are hits to review.
- REVIEW hits are correct in some contexts ("بيرجع 200" in spoken Egyptian) and literal in others; read the sentence and decide.
- Character ranges are built with chr() on purpose: literal escapes were once stripped on save and silently broke whole-word matching. The range covers letters only, so Arabic punctuation counts as a word boundary; keep that one AR line in `scripts/arlint.py`.
- Every SINGULAR hit is rewritten in the plural unless it clearly does not address the learner (for example "مرحلة تقدر" about a stage, "استخدم" in the past tense, or "افتح" inside a quoted UI label). TRAP hits are always rewritten.
- The list is a floor, not a ceiling. Also read every paragraph aloud and ask: would a person say it this way, would a newcomer understand it, does each expression make sense here.
- Fresh eyes: humanize-writing section 4 step 3, with the Arabic text alone. Fix what it finds.
- Every odd phrase a reviewer flags is added to `TRAPS` in `scripts/arlint.py`, the only copy.

## 7c. Humanize check (blocking)

Every text the owner will publish or read (scripts, speaker notes, metadata, playbooks, posts, captions, emails) must carry no recognizable AI writing pattern. Follow the humanize-writing skill:

1. Run `adams check FILE` (it runs `hzlint.py` in the right mode). Extract pptx speaker notes to a .txt first. Rewrite every BLOCK hit; read every REVIEW hit in context.
2. Fresh eyes: humanize-writing section 4 step 3. The Arabic check in 7b and this one can use the same reviewer, asked both questions. Repeat until its verdict is that a reader would not suspect AI.
3. Anything the reviewer or a teammate catches that the lint missed goes into the lint lists in `scripts/hzlint.py`.

## 8. AR/EN parity

- Same page or slide count, same sections in the same order, same tables and diagrams.
- Comparable content density section by section.
- Same numbers, names and sources in both.

## 9. Content checks

- Technical facts verified against sources.md; illustrative figures labeled as illustrative; totals and percentages recomputed; the same figure matches across slides, script and metadata.
- Anything a heading implies is actually shown.
- Do/don't pairs labeled; a "must not" list uses ✗, never ✓.
- No claimed endorsements that do not exist; official documents only commit to real practice.
- Brand: only the project's own brand name, legal entity and domain; retired names go in the profile's `banned_terms`.
- For batch work done by agents, run these checks across every file yourself afterwards.
- Lesson script PDF: one page per slide in deck order; page count equals slide count; page N shows slide N's number, title and thumbnail, followed by the same text as that slide's speaker notes.

## 10. Delivery report (always)

- What changed.
- What was verified, and how.
- The proof (for example: rendered and inspected all slides; measured title check found 0 wrapped titles; broken-line check found 0 single-word last lines; Arabic language check found 0 singular or trap hits and the fresh-eyes review raised nothing open; humanize lint found 0 BLOCK hits and the AI-pattern review raised nothing open; lint returned 0 hits; all contrast pairs at or above 4.5:1).
- What remains, and anything that could not be done or verified, stated plainly.
- Saved files: a file counts as saved on the owner's machine only after its md5 there matches the local copy. Copy first, commit after the copy finishes (never in the same parallel step), then compare.

Do not leave render sheets, lint output or scratch files in the user's own folders.