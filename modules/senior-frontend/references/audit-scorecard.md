# Audit scorecard

Load at phase 1 (Audit) of the SaaS revamp program. The audit judges the running product, not the repo. Trust runtime: what renders at a route, at 375 and 1280, signed in as each role. Docs, comments, tickets, green CI and code reading alone are claims, not evidence. A capability that cannot be shown working is "unproven", and unproven is a finding.

## Evidence rule

Every score and every issue cites runtime evidence: the route, the role, the width, the state, and what rendered (screenshot path or the text and values seen), plus the file that renders it when known. Code reading may locate a cause; it never proves behaviour. Use a test account per role. Never audit with a real customer account, never read secrets, never change production data.

Method per surface: open the route, trigger the 5 states (empty, loading, error, success, connected), try the primary task end to end, then check network and console. Record numbers as seen, with the date.

## 12 lenses, each scored /100, never averaged

Report as a table, one row per lens. Never compute one overall number (an average hides a Critical). Each row: Lens | Score /100 | Evidence | Gap | Action.

| Lens | Question it answers | Look at |
|---|---|---|
| Clarity | Does a new visitor or member know what this is, who it is for and what to do next within 5 seconds? | hero, page titles, empty states, nav labels |
| Value proof | Does it show real output and what it earned, with true numbers only? | results, reports, proof blocks, examples labelled "Example workspace" |
| Friction | How many steps, fields and decisions stand between the user and the goal? | signup, setup, connectors, checkout, cancel |
| Trust | Would a careful buyer believe it? Pricing, privacy, security, legal, data handling, no invented proof | pricing, legal pages, footers, consent, errors |
| Activation | Does a new member reach the first real value fast, and is it measured? | setup, first result, time to first value, events |
| Habit | Is there a true reason to return weekly (changes, alerts, reports)? | dashboard home, emails, notifications |
| Monetization | Are upgrade moments tied to real limits and value, with honest pricing? | pricing, upgrade prompts, billing |
| Retention | Is value summarised, cancel honest, churn reason captured? | monthly summary, billing, cancel flow, lifecycle emails |
| Truth | Zero-trust data, no fabricated numbers, secrecy of methods, labels on demo data | every number on every page, public pages, docs |
| Consistency | One dashboard template, same patterns, tokens only, one vocabulary | dashboards, settings, admin, design tokens |
| Accessibility | WCAG 2.2 AA: contrast, keyboard, focus, targets, forms, reduced motion | each template, forms, modals |
| Performance | LCP under 2.5 s, INP under 200 ms, CLS under 0.1, bundle budgets | key routes, measured |

Scoring bands: 90-100 production grade; 75-89 minor gaps; 60-74 real gaps, plan work; below 60 redesign. A lens cannot score above 74 without runtime evidence recorded.

## Nielsen's 10 heuristics

Score each /100 in a second table, same evidence rule, never averaged:
1. Visibility of system status (status line, last updated, loading)
2. Match between system and the real world (customer vocabulary)
3. User control and freedom (undo, cancel, back, export)
4. Consistency and standards (one template)
5. Error prevention (confirmations, validation, safe defaults)
6. Recognition rather than recall (visible next step)
7. Flexibility and efficiency of use (shortcuts, depth on demand)
8. Aesthetic and minimalist design (focus law, max 3)
9. Help users recognise, diagnose and recover from errors (what happened, how to fix)
10. Help and documentation (every action links to an article)

## Verdict per capability

For every capability (a product, a page family, a flow), one verdict with the reason:

| Verdict | Use when |
|---|---|
| Preserve | Works, true, consistent. Leave it. |
| Redesign | The job is right, the surface fails a lens (clarity, friction, consistency). Same data and logic, new surface. |
| Rebuild | The logic or data is wrong, unproven or a shell. Start from the job. |
| Remove | No job, duplicate, or unprovable (page count is never a goal). Redirect, do not leave a dead route. |

Classification of what you saw: validated, partial, broken, shell (UI with nothing behind it), unproven.

## Issue record

One record per issue, in the audit file and as tasks in `track.md`:

| Field | Content |
|---|---|
| id | `ISS-001` |
| severity | Critical (data loss, security, money, a lie shown to a customer), High (core flow broken or blocked, legal or trust risk), Medium (friction, inconsistency, partial), Low (polish) |
| lens | one of the 12 |
| evidence | route, role, width, state, what rendered, screenshot path |
| impact | who is hurt and how (customer, revenue, trust, data, reliability) |
| fix | the change, in one or two lines |
| verification | how it will be proven after the fix (route, state, measured value, event firing) |

Severity decides order. Critical and High block the final verdict.

## Gap grep (to locate, never to prove)

TODO, FIXME, HACK, TEMP, mock, stub, placeholder, fake, demo, hardcoded, bypass, disabled, "coming soon", console.log, skipped tests, empty catch, orphan routes. Each hit that surfaces at runtime becomes an issue with runtime evidence.

## Audit output

1. Scope: routes, roles, widths, date, what was not covered.
2. Lens table (12 rows) and heuristics table (10 rows).
3. Capability verdicts.
4. Issues by severity.
5. At most 3 next tasks (focus law); the rest live in `track.md`.
