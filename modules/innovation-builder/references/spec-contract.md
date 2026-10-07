# Spec Contract Reference

## TEMPLATE_SPEC Schema

```json
{
  "template_name": "string (kebab-case-friendly)",
  "template_type": "worksheet | canvas | matrix | planner | scorecard | assessment | mapping_tool | framework | calculator",
  "template_purpose": "string",
  "audience": "string",
  "primary_use_case": "string",
  "user_flow": ["step 1", "step 2", "step 3"],
  "title": "string",
  "subtitle": "string (optional one-line description shown below the title)",
  "metadata_fields": [
    {
      "id": "owner",
      "label": "Owner",
      "type": "text",
      "placeholder": "Founder name"
    },
    {
      "id": "date",
      "label": "Date",
      "type": "text",
      "placeholder": "YYYY-MM-DD"
    },
    {
      "id": "stage",
      "label": "Stage",
      "type": "text",
      "placeholder": "e.g. Pre-Seed, Seed, Series A"
    }
  ],
  "sections": [
    {
      "id": "context",
      "title": "Context",
      "purpose": "Why this section exists and what strong content looks like",
      "input_mode": "textarea | input | mixed",
      "placeholder": "Meaningful prompt text that guides the user's thinking",
      "rows": 5,
      "span": "full | half | third | quarter",
      "required": true,
      "group": "optional group name for collapsible grouping"
    }
  ],
  "optional_sections": [],
  "structural_notes": "string or none",
  "design_priorities": ["more executive", "more analytical"],
  "footer_text": "string (optional small footer line for branding or version)"
}
```

`optional_sections` uses the same object schema as `sections`.

---

## Silent Pre-Flight Checklist

Before generating, silently resolve all of the following:

1. Normalize blank or missing optional values to sensible defaults.
2. Never leave unresolved placeholders like `[TEMPLATE NAME]` in the output.
3. Improve section naming, grouping, and order when it materially improves usability.
4. Preserve the original intent of the template.
5. Generate helper text when it is not explicitly supplied.
6. Omit empty containers (no metadata-row if no metadata, no optional-sections if none).
7. Derive `wrapperId` from `template_name` in kebab-case.
8. Scope all CSS, DOM queries, event handlers, and storage keys to `wrapperId`.
9. Build as progressive enhancement: static document first, JavaScript second.
10. Never ask follow-up questions.
11. If the template has more than 10 sections, apply section grouping rules.
12. Default metadata includes Owner, Date, and Stage unless overridden.

---

## Structural Blueprint

The HTML structure must follow this exact nesting order:

```
<div id="[wrapperId]">
  <style> ... all CSS scoped under #[wrapperId] ... </style>

  <div class="toolbar" data-no-export>
    [Save status indicator]
    [Progress indicator if 10+ sections]
    [Clear button]
    [Download JSON button]
    [Download PDF button]
  </div>

  <div class="main-shell">
    <div class="export-area" data-export="true">

      <div class="title-block">
        <h2>[Title]</h2>
        <p class="subtitle">[Subtitle]</p>  (only if subtitle exists)
      </div>

      <div class="metadata-row">  (only if metadata fields exist)
        [metadata input fields]
      </div>

      <div class="toc" data-no-export>  (only if 10+ sections with groups)
        [table of contents links]
      </div>

      <div class="framework-grid">
        [section blocks or section groups]
      </div>

      <div class="optional-sections">  (only if optional sections exist)
        [optional section blocks]
      </div>

      <div class="footer-line">  (only if footer_text exists)
        <p>[footer_text]</p>
      </div>

    </div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
  <script> ... all behavior scoped to #[wrapperId] ... </script>
</div>
```

---

## Title Block Structure

```html
<div class="title-block">
  <h2>Business Model Canvas</h2>
  <p class="subtitle">Map the nine building blocks of your venture in one view.</p>
</div>
```

The subtitle is optional. Omit the `<p class="subtitle">` entirely when no subtitle
is provided. The subtitle should be a single sentence explaining what the tool helps
the user accomplish.

---

## Section Block Structure

```html
<div class="section-block span-[full|half|third|quarter]" data-section="[id]">
  <div class="section-heading">
    <h3>[Section Title]</h3>
    <button type="button" class="helper-toggle" data-no-export
            aria-expanded="false" aria-controls="helper-[id]">+</button>
  </div>
  <div class="helper-panel" id="helper-[id]" data-no-export>
    <p><strong>How to think:</strong> [specific guidance]</p>
    <p><strong>AI prompt:</strong> [copy-paste-ready prompt]</p>
  </div>
  <label for="field-[id]" class="sr-only">[Section Title]</label>
  <textarea id="field-[id]" name="field-[id]" data-field="[id]"
            rows="[rows]" placeholder="[meaningful placeholder]"></textarea>
</div>
```

For `input_mode: mixed`, use both a short `<input>` and a `<textarea>`:

```html
<div class="section-block span-half" data-section="decision">
  <div class="section-heading">
    <h3>Decision</h3>
    <button type="button" class="helper-toggle" data-no-export
            aria-expanded="false" aria-controls="helper-decision">+</button>
  </div>
  <div class="helper-panel" id="helper-decision" data-no-export>
    <p><strong>How to think:</strong> [guidance]</p>
    <p><strong>AI prompt:</strong> [prompt]</p>
  </div>
  <label for="field-decision-label" class="sr-only">Decision label</label>
  <input type="text" id="field-decision-label" name="field-decision-label"
         data-field="decision-label" placeholder="State the decision in one sentence">
  <label for="field-decision" class="sr-only">Decision reasoning</label>
  <textarea id="field-decision" name="field-decision" data-field="decision"
            rows="5" placeholder="Explain the reasoning and evidence behind this decision."></textarea>
</div>
```

---

## Section Group Structure (10+ sections)

When a template has more than 10 sections, wrap related sections in groups:

```html
<div class="section-group" data-group="discovery" data-no-export-collapse>
  <div class="group-heading">
    <h3 class="group-title">Discovery</h3>
    <button type="button" class="group-toggle" aria-expanded="true"
            aria-controls="group-body-discovery" data-no-export>&#9660;</button>
  </div>
  <div class="group-body" id="group-body-discovery">
    [section blocks inside this group]
  </div>
</div>
```

The group toggle collapses or expands the group body. All groups start expanded.
The `data-no-export-collapse` attribute tells the PDF export to force-expand all
groups before capture.

---

## Footer Structure

```html
<div class="footer-line">
  <p>Powered by Your Brand</p>
</div>
```

The footer is a single small line of text at the bottom of the export area.
Style: 10px font, #999 color, centered, with 12px top padding and a thin top border.

---

## CSS Scoping Pattern

All CSS must be scoped under the wrapper ID:

```css
#[wrapperId] { ... }
#[wrapperId] .toolbar { ... }
#[wrapperId] .section-block { ... }
```

Neutral system font stack:
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
```

Spacing system: use multiples of 4px (4, 8, 12, 16, 20, 24, 32).
Border weights: 2px for the outer shell, 1px for all internal divisions.

---

## Grid System

```css
#[wrapperId] .framework-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}
#[wrapperId] .span-full { grid-column: 1 / -1; }
#[wrapperId] .span-half { grid-column: span 1; }
#[wrapperId] .span-third { grid-column: span 1; }
#[wrapperId] .span-quarter { grid-column: span 1; }
```

Three-column grid (when needed):
```css
#[wrapperId] .framework-grid.grid-three { grid-template-columns: 1fr 1fr 1fr; }
```

Four-column grid (when needed):
```css
#[wrapperId] .framework-grid.grid-four { grid-template-columns: repeat(4, 1fr); }
```

Responsive collapse at 768px:
```css
@media (max-width: 768px) {
  #[wrapperId] .framework-grid,
  #[wrapperId] .framework-grid.grid-three,
  #[wrapperId] .framework-grid.grid-four {
    grid-template-columns: 1fr;
  }
  #[wrapperId] .span-half,
  #[wrapperId] .span-third,
  #[wrapperId] .span-quarter {
    grid-column: 1 / -1;
    border-right: none;
  }
}
```

---

## JavaScript Behavior Contract

### Auto-Save

```
- Listen for input events on all [data-field] elements inside the wrapper
- Debounce saves at 300ms
- On save: collect all field values into one JSON object keyed by data-field value
- Wrap in an envelope: { version: 1, timestamp: ISO string, fields: { ... } }
- Store under localStorage key: wrapperId + "__v1"
- Update status: "Saving..." then "Saved"
```

### Restore

```
- On DOMContentLoaded, check localStorage for wrapperId + "__v1"
- If found, parse the envelope and populate matching fields from the fields object
- Silently skip any fields in saved data that no longer exist in the DOM
- Update status: "Draft restored"
- If localStorage is unavailable, show: "Auto-save unavailable" and continue
```

### Reset

```
- On Clear button click, show confirm("Clear all fields and saved data?")
- If confirmed: clear all [data-field] elements, remove localStorage key
- Update status: "Reset complete"
```

### Helper Toggle

```
- On helper-toggle click: read aria-expanded
- If "false": close all other open helpers, open this one, set aria-expanded="true",
  change button text to a minus sign
- If "true": close this one, set aria-expanded="false", change button text to "+"
```

### Section Group Toggle (10+ sections only)

```
- On group-toggle click: read aria-expanded
- If "true": collapse the group body (display:none), set aria-expanded="false",
  change arrow to right-pointing
- If "false": expand the group body (display:block), set aria-expanded="true",
  change arrow to down-pointing
```

### Progress Indicator (10+ sections only)

```
- Count all primary [data-field] textareas in the wrapper
- Count how many have a non-empty trimmed value
- Display: "X of Y sections completed"
- Update on every input event
```

### JSON Export

```
- On "Download JSON" click:
  1. Collect all field values (same as auto-save collect)
  2. Create JSON string with 2-space indentation
  3. Create a Blob with type "application/json"
  4. Create an object URL and trigger download
  5. Filename: wrapperId + "-" + YYYY-MM-DD + ".json"
  6. Revoke the object URL after download
```

### PDF Export with Multi-Page Support

```
- On "Download PDF" click:
  1. Set status to "Generating PDF..."
  2. Hide all [data-no-export] elements
  3. If section groups exist, force-expand all group bodies
  4. Capture the export area with html2canvas (backgroundColor: "#ffffff", scale: 2)
  5. Calculate page dimensions:
     - A4 at 2x scale: pageWidth = 595.28 * 2, pageHeight = 841.89 * 2
     - If canvas width > canvas height * 1.4, use landscape orientation
  6. If canvas height <= page height: single page (same as before)
  7. If canvas height > page height: multi-page slicing
     a. Calculate how many pages are needed: Math.ceil(canvasHeight / pageHeight)
     b. For each page, create a temporary canvas that clips the source at the
        correct vertical offset and draws one page-height slice
     c. Add each slice as a new PDF page
  8. Save with filename: wrapperId + "-" + YYYY-MM-DD + ".pdf"
  9. Restore all hidden elements and collapsed groups
  10. Set status to "Saved"
- If html2canvas or jsPDF are not loaded, alert and continue normally
```

---

## Helper Content Quality Standards

Each helper panel must contain exactly two paragraphs.

### Paragraph 1: How to think

Write a coherent paragraph that:
- Explains what the section is designed to capture
- Describes what strong, high-quality content looks like for this section
- Identifies the one or two most common mistakes founders make in this area
- References the startup stage where this section matters most (when relevant)
- Guides the user's reasoning step by step
- Uses plain, professional English accessible to non-native speakers

### Paragraph 2: AI prompt

Write a coherent, copy-paste-ready prompt that:
- Frames a realistic startup scenario the user can customize
- Asks for structured, specific output (not open-ended brainstorming)
- References relevant frameworks or methods when appropriate
- Ends with a clear request for a deliverable the user can paste into the section
- Uses bracket placeholders like [your product], [target customer], [current stage]

---

## Visual Rules Summary

| Allowed | Prohibited |
|---|---|
| Black (#000) and white (#fff) only | Any color (no blue, green, red, etc.) |
| Helper panel background: #f5f5f5 | Shadows, gradients, glass effects |
| Sharp borders (1px and 2px) | Rounded corners (no border-radius) |
| Strong typographic hierarchy | Icons, illustrations, badges, emojis |
| Balanced whitespace (4px multiples) | Dashboard, card, or app styling |
| Grid logic with precise alignment | Decorative or playful elements |
| Document-like monochrome aesthetic | Marketing or landing-page styling |

---

## Responsive Rules

At screens below 768px:
- Collapse all grid columns to single column
- Preserve section order and hierarchy
- Stack metadata fields vertically
- Keep textareas full width
- Keep toolbar horizontally scrollable if needed
- Keep all controls accessible and tappable (minimum 44px touch target)

---

## Final Reminders

1. The output is a component block, not a full HTML page.
2. No `<!DOCTYPE>`, `<html>`, `<head>`, or `<body>` tags.
3. The outer `<div>` wrapper is the root element of the output.
4. All CSS is inside one `<style>` tag within the wrapper.
5. All behavior is inside one `<script>` tag within the wrapper.
6. External script tags for html2canvas and jsPDF sit before the behavior script.
7. No comments anywhere in the output (HTML, CSS, or JS).
8. No citations anywhere in the output.
9. No explanatory text outside the code block.
10. The code block is the only output.
