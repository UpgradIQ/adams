# Innovation Builder

## What This Skill Does

This skill compiles a template specification into one production-ready HTML/CSS/JavaScript
component block for a structured startup innovation tool. The component behaves like a
premium working document first and an interactive tool second.

The output is always a **component block**, never a full HTML page. No `<!DOCTYPE>`, no
`<html>`, no `<head>`, no `<body>` tags. Just the component: one `<div>` wrapper containing
a `<style>` tag, the HTML structure, external `<script src>` tags for PDF libraries, and
one `<script>` tag for behavior.

Before generating any component, read both reference files:
- `references/spec-contract.md` for the structural contract, visual system, interaction
  model, PDF export, multi-page handling, JSON export, large template rules, anti-patterns,
  and output validation checklist.
- `references/template-catalog.md` for the canonical section structures of 230 startup
  innovation tools organized by domain. When the user requests a known template by name,
  use the catalog entry as the starting specification.

---

## Priority Order

1. Thinking clarity and logical sequencing
2. Practical completion for real startup work
3. Static HTML completeness (works without JavaScript)
4. Reliable interactive behavior
5. Clean multi-page PDF export
6. Monochrome professionalism
7. Responsive readability

---

## Input Handling

The user may provide input in one of three forms:

### Form A: Structured JSON Spec
A JSON object with defined fields. See `references/spec-contract.md` for the schema.

### Form B: Natural Language Description
Extract these fields from the description, filling gaps with reasonable defaults:
- template_name, template_type, template_purpose, audience, primary_use_case
- user_flow (the logical thinking sequence)
- title, subtitle (optional one-line description of the tool's purpose)
- metadata_fields (default: Owner, Date, Stage)
- sections (derive from the description)
- optional_sections, structural_notes, design_priorities, footer_text

### Form C: Template Name Only
The user gives a name like "Business Model Canvas" or "Unit Economics Worksheet".
Look up the template in `references/template-catalog.md` first. If found, use the
catalog entry as the base specification. If not found, use domain knowledge to derive
a complete specification. Build the best possible version of that template.

In all three forms:
- Normalize blank or missing optional values to sensible defaults.
- Never ask follow-up questions.
- Never leave unresolved placeholders.
- Improve section naming, grouping, and order when it materially improves usability.
- Preserve the original intent of the template.
- Generate helper content when not explicitly supplied.

---

## Layout Heuristics

| Template Type | Layout Logic |
|---|---|
| Worksheet or Planner | Sequential vertical flow, mostly full-width or two-column rows |
| Canvas or Framework | Balanced multi-block grid with a clear synthesis or decision area |
| Matrix or Assessment | Rigid grid or table-like structure with labeled axes or criteria |
| Scorecard | Criteria-led structure with rating, evidence, implication, and action |
| Mapping Tool | Source-to-output, current-to-target, stage-to-stage, or dependency flow |
| Calculator | Input fields at top, computed output display at bottom, clear formula logic |

Use one or two columns for narrative logic. Use three or four columns only when
simultaneous comparison is essential. Structural notes override these heuristics.

---

## Large Template Handling

When a template has more than 10 sections, apply these rules:

1. **Group sections into collapsible categories.** Wrap related sections in a
   `<div class="section-group">` with a group heading that toggles visibility.
   Each group starts expanded. The user can collapse groups they have finished.
2. **Add a progress indicator** in the toolbar showing "X of Y sections completed"
   (a section counts as completed when its primary field is not empty).
3. **Add a compact table of contents** above the framework grid listing all section
   group names as anchor links.
4. Groups, table of contents, and progress indicator must be excluded from PDF export.
   The PDF captures all sections fully expanded regardless of collapse state.

---

## Non-Negotiable Structure

Every component must contain exactly:

1. One outer `<div>` wrapper with one unique ID (derived from template_name in kebab-case)
2. One toolbar (sits outside the export area)
3. One main bordered shell
4. One export area marked with `data-export="true"`
5. One title block (with optional subtitle)
6. One metadata area (only when metadata fields exist)
7. One main framework area
8. One optional section container (only when optional sections exist)
9. One optional footer line (only when footer_text is provided)

The toolbar sits outside the export area. The title block, metadata, framework grid,
optional sections, and footer sit inside the export area. The visible structure, labels,
inputs, textareas, section headings, and major boxes must exist in static HTML before
JavaScript runs.

---

## Component Rules

### Form and Content
- Use `<textarea>` for long-form content, `<input type="text">` for short fields
- Never use `contenteditable`
- Every editable field must have a label, `id`, `name`, and `data-field` attribute
- Use meaningful placeholder text that guides thinking, never generic filler
- When `input_mode` is `mixed`, use one short input and one textarea

### Visual System
- Monochrome only: black (#000) and white (#fff)
- Helper panel background: #f5f5f5 with #000 text (minimum 15:1 contrast ratio)
- No color, gradients, rounded corners, shadows, icons, illustrations, badges, glass
- Sharp borders, strong typographic hierarchy, balanced whitespace, precise grid logic
- Flat, minimal, serious, document-like
- Neutral system font stack
- Consistent spacing system (multiples of 4px) and consistent border weights

### Helper System
- Each major section heading includes a small `+` button aligned to the top-right
- The button toggles a helper panel inside the same section
- Only one helper panel may be open at a time
- No helper panel open by default
- Helper panels hidden by default through CSS (`display: none`), not JavaScript alone
- Each helper panel contains exactly two paragraphs:
  1. `How to think:` specific guidance for completing this section well
  2. `AI prompt:` a copy-paste-ready prompt the user can use in any AI tool
- Helper content must reference startup-relevant context: mention the startup stage
  where this section matters most, reference common founder mistakes for this area,
  and frame the AI prompt around a real startup scenario
- Helper buttons and panels excluded from PDF export via `data-no-export`

### State Management
- All editable fields auto-save to localStorage
- Storage key: `wrapperId + "__v1"` (include version for future migration)
- Restore saved content on reload
- Visible save-status element with `aria-live="polite"`
- Status states: `Auto-save enabled`, `Saving...`, `Saved`, `Draft restored`, `Reset complete`
- Debounce saves (300ms) for smooth typing
- Clear/Reset button with confirmation dialog
- Graceful fallback when localStorage is unavailable: show "Auto-save unavailable"

### JSON Export
- Include a "Download JSON" button in the toolbar alongside "Download PDF"
- On click: collect all field values into a JSON object, create a Blob, trigger download
- Filename: `wrapperId + "-" + YYYY-MM-DD + ".json"`
- The JSON export enables founders to back up, transfer, or share their work

### PDF Export
- Include "Download PDF" button in toolbar
- Use html2canvas and jsPDF through valid external `<script src>` tags
- Show "Generating PDF..." in the status indicator during capture
- Export only the marked export area
- Exclude all `[data-no-export]` elements
- White background, centered capture, scale: 2

**Multi-page handling:** After capturing the export area with html2canvas, measure the
canvas height against the PDF page height. If the canvas exceeds one page:
1. Calculate page dimensions (A4: 595.28 x 841.89 points)
2. Slice the canvas into page-height segments
3. Add each segment as a separate PDF page
4. Use portrait orientation for most templates, landscape only when the layout width
   exceeds 1.4 times the layout height

- Dynamic filename: `wrapperId + "-" + YYYY-MM-DD + ".pdf"`
- Component must work normally if PDF libraries fail to load

### WordPress Compatibility
- Works inside a WordPress Custom HTML block
- Only HTML, CSS, and vanilla JavaScript
- No React, Vue, jQuery, Bootstrap, Tailwind, or any framework
- Scope all CSS under the unique wrapper ID
- No reliance on theme defaults
- Valid script tags only

### Accessibility
- Semantic HTML elements
- `<button type="button">` for non-submit controls
- Labels associated with inputs (visually hidden via sr-only class)
- `aria-expanded` and `aria-controls` on helper toggle buttons
- `aria-expanded` on section group collapse toggles
- Visible focus styles: 2px solid #000 outline with 2px offset
- Full keyboard navigation

---

## Common Mistakes to Avoid

These are patterns that degrade output quality. Check for them before finalizing.

1. **Full HTML page wrapper.** Never output `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>`.
   The output is a component block starting with `<div id="...">`.
2. **Generic placeholder text.** "Enter text here" or "Type something" is not acceptable.
   Every placeholder must guide thinking: "Describe the specific customer segment, their
   primary pain point, and how they currently solve it."
3. **Dashboard or app-card styling.** No colored headers, card shadows, rounded corners,
   gradient backgrounds, or icon badges. This is a monochrome working document.
4. **Helper content that repeats the section title.** "This section is about Context"
   adds zero value. Explain what strong content looks like and what common mistakes to
   avoid for that specific section.
5. **Single-page PDF for large templates.** Templates with more than 6 sections will
   overflow a single PDF page. Always implement multi-page slicing.
6. **Unscoped CSS.** Every CSS rule must be prefixed with `#[wrapperId]`. Bare class
   selectors like `.toolbar { }` will conflict with the WordPress theme.
7. **contenteditable usage.** Never use contenteditable. It breaks auto-save, produces
   inconsistent HTML, and does not work reliably across browsers. Use textarea and input.
8. **Missing data-field attributes.** Every editable element must have `data-field` for
   auto-save to work. If a field has no `data-field`, its content will be lost on reload.
9. **Inline event handlers.** Never use `onclick="..."` in HTML. Attach all event
   listeners in the script block using addEventListener.
10. **Raw CDN URLs as visible text.** Script src tags must be valid HTML elements, not
    printed as visible text on the page.

---

## Output Validation Checklist

Before finalizing, verify every item:

1. Output is exactly one code block
2. Output contains NO `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>` tags
3. Output starts with the outer wrapper `<div id="...">`
4. One outer wrapper with unique ID exists
5. One toolbar exists (outside export area)
6. One main shell exists
7. One export area exists with `data-export="true"`
8. One title block exists (with subtitle if provided)
9. Metadata area exists only when metadata fields are defined
10. Main framework area exists
11. Optional section container exists only when optional sections are defined
12. Footer line exists only when footer_text is provided
13. One `<style>` tag is included, scoped under wrapper ID
14. Valid external `<script src>` tags for html2canvas and jsPDF
15. One `<script>` tag handles all behavior
16. No HTML, CSS, or JS comments exist in the output
17. No citations or explanatory text exist in the output
18. No duplicate IDs exist
19. No unresolved placeholder tokens like `[TEMPLATE NAME]` exist
20. No malformed HTML, CSS, or JavaScript
21. Every major section has an editable textarea or input with `data-field`
22. Each helper panel contains exactly two paragraphs (How to think + AI prompt)
23. Helper toggle works on repeated click (open/close)
24. Opening one helper closes any other open helper
25. Auto-save works with debounced localStorage writes
26. Restore populates fields on reload
27. Reset clears fields and localStorage after confirmation
28. JSON export downloads a valid JSON file of all field values
29. PDF export produces a multi-page PDF when content exceeds one page
30. PDF export shows status feedback during generation
31. Static layout is fully usable without JavaScript
32. All CSS rules are scoped under the wrapper ID
33. For templates with 10+ sections: section groups, progress, and TOC exist

---

## Output Contract

Return exactly one code block containing the complete paste-ready HTML component block.

Do not:
- Wrap in a full HTML document
- Include `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>` tags
- Add explanatory text before or after the code block
- Add comments inside the code
- Add citations
- Add markdown outside the code block
- Describe the process
- Ask questions
- Provide alternatives

The output must be directly pasteable into a WordPress Custom HTML block and render
correctly without any modification.
