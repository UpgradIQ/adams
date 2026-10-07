# Page standards for a SaaS

Load at the Plan and Execute phases of the revamp program. Values (width, line counts, last line rules) come from the canonical table in `modules/line-balance/GUIDE.md` and the project's `DESIGN.md`. Colours and spacing from tokens only. Truth rules from `modules/product-principles/GUIDE.md`. Consistency inside the product, variety on marketing pages only. A page needs a job; page count is never a goal.

## 1. Marketing page anatomy

Each page has one thesis and one primary CTA. Order:

1. **Hero thesis:** one sentence that names the customer and the outcome (2 lines max), one supporting line, one CTA, a real visual (the product's own output or a labelled "Example workspace").
2. **Proof:** what the product actually did or can show now. Real counts with an as-of date, real permitted quotes, the product's own output. With none, a labelled example. Never invented logos, quotes, ratings or certifications.
3. **How it works:** 3 steps at most, outcome first.
4. **Objection:** the real hesitations (price, setup effort, data safety, lock-in, fit), each answered next to the CTA and linked to the docs article.
5. **One CTA:** repeated, same label, same destination. Outcome-based label ("Run my site test").

Variety: layout, mockups and rhythm may differ page to page. Section count follows the content (no minimums). Do not publish pages for things that do not exist (Investor Relations, Press, Certifications, Customer stories) until real content does.

Do not publish methods: no scoring factors, weights, formulas, or how a feature is cheaply built.

## 2. Pricing page standard

- Plans from the plan table (never typed by hand): name, price, currency, billing period, tax note, what changes for the customer, limits as numbers from the table.
- 3 plans (Starter, Pro, Growth), recommended plan visible with a plain reason. Annual saving computed from the real prices.
- Compare on outcomes first, features second; one comparison table, text left and numbers right, one line per cell.
- Risk reversal in plain words: 7-day Pro trial, the date of the first charge, reminder before it, cancel in one click, refund terms exactly as they are.
- FAQ answers real objections, each linking to an article.
- Banned: fake "was" prices, hidden fees, pre-checked add-ons, countdowns (see `dark-patterns.md`).
- Experiment record for every change (hypothesis, metric event, readout date, ICE).

## 3. Onboarding and setup standard

- Email and password only. No social login.
- Ask only what changes the product: stage and role (once). Everything else later.
- One rung per screen (commitment ladder). Each step says what it unlocks and how long it takes.
- Checklist starts truthfully: steps already done are shown done (endowed progress); progress moves only on measured events.
- First value as early as possible: the free test result carries into the account.
- Every step has the 5 states. A failed connector shows what happened and how to fix it, with a link to the article.
- Setup is resumable and skippable; skipped steps return as one item on the dashboard, never as a modal.
- Events: `setup_step_completed`, `connector_connected`, `activation_reached`.

## 4. Dashboard template in detail

One template for every dashboard page. No per-page layout inventions.

```
[ Title ]  one-line purpose  [ How to ]
[ Status: state · last updated 12:40 ]
[ Tab ][ Tab ][ Tab ][ Tab ]            (max 4)
-----------------------------------------------
Main: what to do now (max 3 items, in order)
Details on demand (expand, drawer, or tab)
```

- **Title and purpose:** title is a noun (the thing), purpose is one line that never wraps. "How to" opens the docs article for this page.
- **Status line:** the state (for example Connected, Needs attention, Paused) plus last updated time from data, never a made-up time.
- **Tabs:** max 4. If a fifth is needed, merge or move depth into the first tab's details.
- **Main:** the next 3 actions maximum, ranked, each with an outcome-based button. No wall of problems. Remaining items are one click away.
- **Admin pages use the same template** with admin density; same header, status line and tabs rules.
- Tables: text columns left, number columns right (tabular figures), header aligned with its column, one line per cell, headers nowrap, expand and collapse as explicit bordered + and - controls.
- Charts: tokens only, series order fixed, 6 series max, axes labelled with units and time range.
- Numbers come from the database with a date; if there is none, say "No data yet" and invite the action that creates it.

## 5. The five states (every screen)

| State | Standard |
|---|---|
| Empty | An invitation to act, not "No data". One sentence of what appears here once there is data, one button. |
| Loading | Skeleton in the final layout. No spinner-only screens. No layout shift. |
| Error | What happened, how to fix it, one retry or link. No apology, no stack trace, no blame. |
| Success | A small celebration (icon, line of text) and the next step. No confetti walls. |
| Connected | Proof, not a badge. See section 6. |

Every state is designed, reachable in a test, and checked at 375 and 1280.

## 6. Connector and integration hub plus detail page

**Hub (`Settings > Integrations` or the product's connectors page):** one card per source, equal height, status chip (Not connected, Connected, Needs attention), one button. Cards in a row have equal line counts.

**Detail page (same template as the dashboard):**
- Not connected: what connecting unlocks, what access is requested and why, how long it takes, Connect button, docs article.
- **Connected state (the rule):** proof that it works:
  - last read time,
  - 3 real values read from the source (for example the property name, the most recent date with data, a count),
  - what it unlocked (named products or features, linked),
  - Test now and Reconnect buttons,
  - saved settings shown as values with an Edit button.
- Never show an empty field beside "Connected". If a value is unknown, show it as "Not set" with Edit, or hide the row.
- Error: what the source returned, the fix, Reconnect.
- Events: `connector_connected`, `connector_failed`, `connector_tested`.

## 7. Settings rules

- Personal options: Settings (profile, password, notifications, appearance, privacy, export and delete).
- Workspace options: Settings > Workspace (name, members and seats, billing, integrations, branding).
- A product's own options: only in that product's Settings tab (for example Monitor frequency lives in Monitor).
- Never the same option in two places. Each setting links to its docs article.
- Billing: plan, next charge date, invoices, pause, downgrade, cancel in one click plus one confirm.
- Privacy: honour DNT and GPC, no consent banner (owner decision), legal pages truthful and current.

## 8. Docs center standard (Stripe Docs style)

Hierarchy: Getting started, Connect each source, each product (Score, Diagnosis, Monitor, Competitors, Roadmap, Experiments, Results, Reports, Advisor), Settings, Team and Billing, Troubleshooting, Glossary.

- Every action, connector, setting and error state has an article. The product links to it ("How to", "Learn how to fix this").
- **A build test fails if a linked article is missing.** Registry of article slugs is the single source; UI links are generated from it.
- Article anatomy: one-line purpose, prerequisites, numbered steps, what you should see, common problems with fixes, related links. Short and scannable.
- Docs describe what the product does for the customer. Never document scoring factors, weights or cheap-build methods.
- Changelog lists only shipped changes.

## 9. Copy rules

- English, sentence case, no em dash or en dash (use comma, colon, `·`, or rewrite), Latin digits.
- Outcome-based labels. Never "Submit", "Click here", "Learn more" without an object.
- Brand: the project's own name only.
- Short text never wraps: titles, labels, chips, buttons, nav items, bullets, stat captions are one line at the real width. Fix by rewording.
- Paragraphs: no orphan last line (>= 30% of the line on web). Card body 2 lines.
- Errors: what happened and how to fix. Success: what happened and what is next.

## 10. Accessibility (WCAG 2.2 AA minimum)

- Semantic HTML before ARIA; one h1 per page; landmarks.
- Contrast 4.5:1 for text, 3:1 for large text and UI components, in light and dark.
- Visible focus, full keyboard path, focus not obscured by sticky bars (2.2), target size at least 24 by 24 CSS px (2.2).
- Forms: labels, errors tied to fields, no placeholder-only labels, no re-entry of data already given (2.2).
- Motion respects `prefers-reduced-motion`. No info by colour alone. Alt text for meaningful images.
- Auth without cognitive tests (2.2): email and password works with password managers and paste.

## 11. Performance budgets

| Metric | Budget (75th percentile, real users where measured, lab otherwise) |
|---|---|
| LCP | under 2.5 s |
| INP | under 200 ms |
| CLS | under 0.1 |
| First Load JS | per the senior-frontend default: 200 KB marketing, 300 KB app |

State the budget before optimising and report the measured delta. Third-party scripts load after page load. No analytics beyond what the project's privacy statement says.
