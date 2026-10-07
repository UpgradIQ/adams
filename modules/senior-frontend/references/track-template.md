# Track: Example SaaS
Project: Example SaaS
Updated: 2026-10-06
Verdict: Not ready

## Next immediate task
T-002 Fix the connector connected state

## Phases
### P1 Audit
Score the running product on 12 lenses with runtime evidence and list every issue.
### P2 Repair
Fix Critical and High issues, dependency-first, one task at a time.
### P3 Conversion
Ship pricing and onboarding changes as experiments with named events.

## Tasks
### T-001 Score the dashboard and settings
- id: T-001
- title: Score the dashboard and settings
- phase: P1
- status: verified
- evidence: /dashboard and /settings/integrations walked as member and admin at 375 and 1280; 9 open items shown on home; connector shows Connected beside an empty property field
- definition of done: 12 lenses scored with evidence; 10 heuristics scored; every issue recorded with id, severity, lens, evidence, impact, fix, verification; scores not averaged
- risks: admin pages need a test admin account
- next action: none
- agent prompt: Execute only T-001. Update .planning/track.md. Mark verified only if every item in the definition of done holds.

### T-002 Fix the connector connected state
- id: T-002
- title: Fix the connector connected state
- phase: P2
- status: todo
- evidence: /settings/integrations (member, 1280) shows Connected beside an empty property field; file src/components/connector-card.tsx renders the badge from a boolean only
- definition of done: connected state shows last read time, 3 real values read, what it unlocked, Test now and Reconnect; saved settings shown as values with Edit; no empty field beside Connected; checked at 375 and 1280; docs article linked
- risks: source API rate limit during Test now
- next action: read the connector card and the status query
- agent prompt: Execute only T-002. Update .planning/track.md. Mark done only if every item in the definition of done holds, then verify on the running product.

### T-003 Dashboard home shows at most 3 next items
- id: T-003
- title: Dashboard home shows at most 3 next items
- phase: P2
- status: blocked
- evidence: /dashboard (member, 1280) lists 9 open items with equal weight
- definition of done: main area shows at most 3 ranked items; the rest sit behind one control; status line shows state and last updated; at most 4 tabs; balance FLAGGED 0 at 375 and 1280
- risks: blocked by T-002 because the ranking reads connector state
- next action: wait for T-002 to be verified, then read the ranking query
- agent prompt: Execute only T-003 after T-002 is verified. Update .planning/track.md. Mark done only if every item in the definition of done holds.

### T-004 Pricing page experiment: annual saving line
- id: T-004
- title: Pricing page experiment: annual saving line
- phase: P3
- status: todo
- evidence: /pricing (visitor, 1280) shows monthly prices only; annual saving is not shown
- definition of done: saving computed from the plan table; experiment record filled (hypothesis, metric event, readout date, ICE); event plan_viewed and checkout_started fire; passes dark-patterns checklist
- risks: sample too small to read before the readout date
- next action: write the experiment record from funnel-map.md
- agent prompt: Execute only T-004. Update .planning/track.md. Mark done only if every item in the definition of done holds.

## Closure reports
### T-001
Task: T-001 Score the dashboard and settings
What changed: audit recorded, 14 issues listed (see ISS ids in the audit file)
Files: .planning/audit.md
Verification: routes walked as member and admin; screenshots in the scratchpad
Live check: /dashboard, /settings/integrations at 375 and 1280
What is left: repairs tracked as T-002 and T-003
