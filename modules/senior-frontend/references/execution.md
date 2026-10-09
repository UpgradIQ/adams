# The tracker, the task loop and the gates

Load at phases 2 to 5 of the SaaS revamp program. One tracker, one next task, evidence for every claim.

## The single tracker

`.planning/track.md`, gitignored. It is the only source of status. No shadow trackers (Notion, extra todo files, HTML checklists as truth). The HTML page from `scripts/track.py render` is a view of this file, never an input. Repo reality wins: a checkmark, a plan or a commit message is a claim until the running product shows it.

Check it any time: `adams track lint .planning/track.md` (exit 1 on errors). A filled example is `references/track-template.md`.

Lint rule STALE-REVIEW: a task in `review` fails lint when (a) its evidence is empty or "none yet" (add evidence, a PR, branch or file, or set it todo), or (b) its next action asks for owner review or approval and every D-id it cites (next action, definition of done, evidence) is `decided` in the `decisions.md` next to the track file (the question is answered: set it done, or todo if work remains). Rule (b) is skipped when there is no `decisions.md`.

## Statuses (exactly these seven)

| Status | Meaning |
|---|---|
| todo | Not started |
| in-progress | Being worked now |
| blocked | Cannot proceed; the blocker is named in risks |
| review | Built, waiting for verification |
| done | Built and checked by the builder, not yet verified at runtime |
| verified | Definition of done proven against the running product, evidence recorded |
| dropped | Decided not to do, reason in evidence |

Only `verified` counts toward a Ready verdict, with `dropped`.

## Structure

```
# Track: <project>
Project: <name>
Updated: <YYYY-MM-DD>
Verdict: Ready | Ready with gaps | Not ready

## Next immediate task       (exactly one line: task id and title)
## Phases                    (### P1 Name, purpose in one or two lines)
## Tasks                     (### T-001 Title, then the fields below)
## Closure reports           (free form, one block per finished task)
```

Phase order is dependency-first: verify before repair, repair before new features, data, auth and routing before polish, blockers before cosmetics. Each task is atomic.

## Task block fields

```
### T-014 Short title
- id: T-014
- title: Short title
- phase: P2
- status: todo
- evidence: route, role, width, what renders now (or the file that causes it)
- definition of done: 3 or more measurable items, separated by semicolons
- risks: what could go wrong, or the blocker if status is blocked
- next action: one concrete first step
- agent prompt: Execute only T-014. Update .planning/track.md. Mark done only if every item in the definition of done holds.
```

Optional field: `- depends: T-012, T-013` lists the tasks that must be done, verified or dropped first. Lint fails on an unknown id, a self reference or a cycle, and `adams next` lists the todo tasks whose dependencies are met. Edit status in place with `adams track set FILE T-014 review --evidence "PR #123 opened"`.

Definition of done items are measurable ("connected state shows last read time and 3 real values at 375 and 1280"), never "works correctly". Evidence names a route or a file, never "looks fine".

## The task loop

```
open track.md --> Next immediate task --> do ONLY that task --> run gates
      ^                                                           |
      |                                                           v
  set next task <-- update status + closure report <-- verify on the running product
```

1. Read `Next immediate task`. Work only on it.
2. Build to `references/page-standards.md`; conversion changes carry an experiment record.
3. Run the gates below that apply. Fix the class of defect, not one instance.
4. Verify against the running product, record evidence, set `verified` (or `review` if you cannot verify).
5. Write the closure report, choose the next task, run `track.py lint`.
6. Stop. Do not start a second task without being told.

Same approach failing twice: stop and state the root cause before trying again.

## Closure report (per finished task)

```
Task:         T-014 Short title
What changed: one or two lines
Files:        absolute or repo-relative paths changed
Verification: proof (test output, build exit code, measured values, screenshot paths)
Live check:   route, role, width, what was seen on the running product (or "not checked: reason")
What is left: remaining gaps, follow-up task ids, or "nothing"
```

Say plainly what failed or was skipped. Never imply a check that was not run.

## Quality gates

A gate that is missing is itself a finding. Report each as pass, fail or not run (with the reason).

| Gate | Pass means |
|---|---|
| Tests | project test command exits 0 |
| Build | project build exits 0 (its own prebuild gates included) |
| Lint | linter exits 0 |
| Types | typecheck exits 0 |
| Balance | `web_balance` on the changed pages at 375 and 1280 (plus 768 and 1440 for checks) reports FLAGGED 0 |
| Accessibility | WCAG 2.2 AA checks on the changed templates: contrast, keyboard, focus, targets, forms |
| Performance | LCP under 2.5 s, INP under 200 ms, CLS under 0.1 on the changed routes, measured |
| Secrecy | no factors, weights, formulas, internal paths or cheap-build methods visible to a non-admin visitor; no secrets in the response body |
| Persona E2E | the project's persona suite is green (update specs in the same change as behaviour) |
| Live check | the change works on the running product, as each affected role |
| Docs coverage | every new action, connector, setting and error state has an article, and the missing-article build test passes |
| Analytics events | each named event in the experiment or funnel record fires once with the right properties |
| No fabricated data | every number on the changed surfaces comes from data with a date, or is labelled "Example workspace" |
| Owner confirmation | list items needing the owner (money, destructive database change, launch switch, real member account); do them only after an explicit yes in chat |

Deploy and push rules come from the project's `AGENTS.md`. Destructive database changes always need the owner's confirmation.

## Stop rule

Stop the program only when there are 0 Critical and 0 High issues open, every phase's tasks are `verified` or `dropped`, the gates pass or have a stated reason, and the affected areas were re-audited after the fixes.

## Final verdict

| Verdict | Use when |
|---|---|
| Ready | 0 Critical, 0 High, 0 Medium open that affects a customer flow; all gates pass; all tasks verified or dropped |
| Ready with gaps | 0 Critical, 0 High; open Medium or Low items and any gate not run are listed with owners |
| Not ready | any Critical or High open, a core flow unverified, or a gate failing |

Report: verdict, lens table (12 scores, not averaged), issues by severity, gates table, what was not verified, and the next immediate task (one).
