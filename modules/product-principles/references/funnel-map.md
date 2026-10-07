# Funnel map

Load when planning a change meant to move a metric. Stages: visitor > free test > signup > trial > activated > paid > retained > expanded > referral. Event names are a proposed vocabulary (snake_case, verb_object); check the project's analytics plan first and reuse names that exist. Every KPI is computed from real events; a stage with no instrumented event has no number, and the report says "not measured".

## Stages

### 1. Visitor
- **Goal:** the right person understands the thesis in one screen and starts the free test.
- **KPI:** visitor-to-test-start rate = unique visitors with `site_test_started` / unique visitors (per source, per device).
- **Surfaces:** homepage, product pages, pricing, docs, SEO content.
- **Levers:** hero thesis, one CTA, proof from real output, objection answers, load speed.
- **Events:** `page_viewed`, `cta_clicked` (with `cta_id`), `site_test_started`.
- **Typical failure:** several competing CTAs, vague hero, invented proof, slow LCP.

### 2. Free test
- **Goal:** the visitor gets a true, specific finding about their own site.
- **KPI:** test completion rate = `site_test_completed` / `site_test_started`; median time to result.
- **Surfaces:** homepage test, result page.
- **Levers:** fast result, plain finding, one next step, no signup before value.
- **Events:** `site_test_started`, `site_test_completed`, `site_test_failed` (with reason), `result_viewed`.
- **Typical failure:** errors with no fix, result behind a wall, a long list instead of the top 3.

### 3. Signup
- **Goal:** the visitor keeps the result by creating an account (email and password only).
- **KPI:** result-to-signup rate = `signup_completed` / `result_viewed`.
- **Surfaces:** signup, password link email, welcome.
- **Levers:** one field set, clear reason to sign up (save, track, act), sign-in link visible.
- **Events:** `signup_started`, `signup_completed`, `signup_failed` (with reason), `access_email_opened`.
- **Typical failure:** extra fields, unclear email step, link scanners burning a token.

### 4. Trial
- **Goal:** the member starts the 7-day Pro trial or stays on the free level with a clear next step.
- **KPI:** trial start rate = `trial_started` / `signup_completed`.
- **Surfaces:** plan choice, trial start, trial banner, trial emails.
- **Levers:** risk reversal copy (first charge date, reminder, one-click cancel), trial start at a moment of value.
- **Events:** `plan_viewed`, `trial_started`, `trial_reminder_sent`, `trial_ended`.
- **Typical failure:** unclear charge date, trial starts before any value, no reminder.

### 5. Activated
- **Goal:** the member reaches the activation moment: first connected source plus first Roadmap Action opened (the project defines the exact pair in its plan).
- **KPI:** activation rate = members with `activation_reached` within 7 days / members who signed up; time to activation (median).
- **Surfaces:** setup, connectors hub, dashboard home, Roadmap.
- **Levers:** shorter setup, endowed progress, prefill, connected-state proof, one first Action.
- **Events:** `setup_step_completed` (with `step_id`), `connector_connected` (with `source`), `connector_failed`, `action_opened`, `activation_reached`.
- **Typical failure:** connector errors, empty states without an invitation, too many first choices.

### 6. Paid
- **Goal:** the member upgrades when a real limit or a real result makes the next plan obvious.
- **KPI:** trial-to-paid rate = `subscription_started` / `trial_ended`; free-to-paid rate for non-trial members.
- **Surfaces:** pricing, upgrade moments, checkout, billing.
- **Levers:** paywall at the moment of value, plan comparison on outcomes, default plan, risk reversal.
- **Events:** `upgrade_prompt_shown` (with `limit`), `upgrade_prompt_dismissed`, `checkout_started`, `checkout_failed`, `subscription_started`.
- **Typical failure:** hidden price, surprise at checkout, upgrade prompts unrelated to what the member is doing.

### 7. Retained
- **Goal:** the member keeps getting true value every week and month.
- **KPI:** week-4 and month-3 retention = members with a value event in the period / members paid at the start; logo churn and revenue churn from billing data.
- **Surfaces:** dashboard home, lifecycle emails, monthly value summary, Reports, cancel flow.
- **Levers:** triggers on real changes, focus law, monthly summary with real numbers, working cancel with pause and downgrade.
- **Events:** `dashboard_viewed`, `value_event` (Score change seen, Experiment result read, Report opened), `email_clicked`, `cancel_started`, `cancel_completed` (with reason), `subscription_paused`.
- **Typical failure:** no reason to return, noisy emails, hard cancel that hides the real churn reason.

### 8. Expanded
- **Goal:** the member grows usage because the product proved itself: more workspaces, seats, sources, higher plan.
- **KPI:** expansion revenue / starting recurring revenue of the cohort; share of workspaces with 2+ seats.
- **Surfaces:** workspace and team settings, seat packs, plan page.
- **Levers:** invite prompt after a shared result, limit shown honestly, clear price.
- **Events:** `invite_sent`, `invite_accepted`, `seat_pack_started`, `plan_changed` (with `from`, `to`).
- **Typical failure:** invites buried, limits discovered by error instead of shown.

### 9. Referral
- **Goal:** members share something real that helps the receiver.
- **KPI:** referral rate = members with `share_created` / active members; signups from shared links.
- **Surfaces:** shareable Report, public result link, invite flow.
- **Levers:** a shareable Report the member is proud of, link opens to a real free test.
- **Events:** `share_created`, `share_viewed`, `signup_completed` (with `source=share`).
- **Typical failure:** referral asked before value, rewards that pressure.

## Experiment template (every conversion change)

Copy into `.planning/track.md` task evidence or the experiment log. One record per change.

```
id:            EXP-001
stage:         free test
hypothesis:    If <change>, then <metric> will <direction> because <reason from the customer's behaviour>.
metric:        <named analytics event or ratio>, for example site_test_completed / site_test_started
guardrail:     <metric that must not drop>, for example signup_completed / result_viewed
audience:      <who sees it>, split <e.g. 50/50 by visitor id>
readout date:  <YYYY-MM-DD, set at the start, not moved to fit the result>
ICE:           Impact <1-10> x Confidence <1-10> x Ease <1-10> = <score>
decision rule: ship if <threshold>, revert if guardrail drops by <threshold>, else extend once
result:        <filled at readout from real events; "not measured" if the event did not fire>
```

Rules:
- No readout date, no experiment. No event, no experiment.
- Sample too small to read means the result is "inconclusive", never a win. Do not report percentages from tiny samples as findings.
- Ethical check first: the change must pass `dark-patterns.md`.
- One change at a time per stage so the readout means something.
- ICE ranks the queue; it never replaces judgement. Truth beats a high score.
