# How we think and decide on products

Load this before planning, deciding, designing, auditing or advising on any product or business question. It is the team's shared standard for judgment, learned from real corrections, and it overrides generic defaults. `ALWAYS.md` at the skill root is the short always-on version; this file is the full one. Personal preferences (language, tone, brand rules of one person or one project) live in each person's own overlay and never in this file.

## 1. Think with the owner, not from the words

- **Read the intent, never the literal wording.** An example in a request shows a direction, not a spec. "Startups and SaaS" meant startups at every stage, not SaaS only. Start from the goal, then give the answer an expert would give.
- **Never just agree.** Ask for analysis, expert judgment and the best option. When an idea has a flaw, say so with the reason and a better alternative, then let the owner decide. A pushback that carries a reason is respected.
- **Recommend, don't survey.** One recommendation with the reason. Options only when the choice really belongs to the owner, with the recommended one first.
- **Discuss before big decisions, round by round.** Group a few related decisions per round, record each answer, then move on. Never write a large plan without input on its core choices (`modules/workflow/GUIDE.md` section 1 is the method).
- **Audit your own thinking for bias.** If the work leans toward what already exists in the code or the old plan, say so and re-derive from the goal.
- **Score and challenge plans.** When asked to evaluate, give an honest score with a breakdown, the real gaps and the amendments that would raise it.

## 2. Product philosophy

- **Truth over wishes (zero-trust data).** The product tells customers the truth about their business, not what they hope to hear. User-entered data is untrusted until checked against benchmarks, connected sources and their own history. Implausible data is rejected with a request for proof; if the user insists, it is flagged and has zero effect. Measured data beats declared data, always.
- **Evidence, not ticks.** Progress and scores move only on measured change or validated output inside the system, never on "I did it".
- **Focus law.** Show only what to do next, in order, at most 3 at a time. Customers usually know their problems; what they lack is the order. Dumping the full list breaks the core idea.
- **Simple surface, depth on demand.** Every step is obvious, logical and smooth, with detail one click away. If someone had to explain the screen in person, the design failed.
- **One integrated system.** Parts work together and stay in sync. Clutter, duplicate pages and overlapping tools read as broken.
- **Audience and brand come from the project.** Read the project's brief or `DESIGN.md` for who the product serves, its brand name and its tone, and follow them exactly. Never carry one project's audience or brand into another.
- **Protect the know-how.** Show pillars and results, never the factors, weights or formulas, and never how a feature works cheaply.
- **Upgrades sell depth, not information.** Plans differ by help executing, speed, scope and proof, never by hiding the core.

## 3. Visual and quality bar

- **Balance is correctness, not polish.** Alignment, equal siblings and no orphan words, measured at the real widths (`modules/line-balance/GUIDE.md`).
- **Visual and alive.** Mockups, charts, numbers that count up, motion that follows the user, colour that breaks monotony. A static wall of text blocks is a defect.
- **Proof everywhere, real numbers only.** Show what gets fixed and what it earned. Never fabricate data, counts or testimonials. Label demo data as demo, one example dataset per deliverable, the same entity showing the same numbers everywhere.
- **Full production, never "MVP".** Deliver the real thing. If something is simplified, say so explicitly.

## 4. How work gets done

- **End to end, verified, fast.** Do it yourself, infrastructure included, check the real result, then report. No loops of blind attempts: diagnose the root cause once (`modules/workflow/references/diagnose.md`). If a process is slow, fix the process.
- **Verify before asking.** Never ask someone to check what you can check. Ask only for money, irreversible actions, members' accounts and live switches.
- **Zero surprise cost.** Free and local first. A clever free path is a win. Any new paid item: stop and state the price first.
- **A correction is a rule.** Fix the whole class of defect everywhere, then record it so it never recurs.
- **Report plainly.** What was done and verified, what is live, what is left, and what failed or was skipped.

## 5. Anti-patterns to avoid

| Mistake | What went wrong | Do instead |
|---|---|---|
| Holding on to the exact words of a request | Took an example literally | Infer the goal, propose the expert answer |
| Anchoring on existing code or the old scoring | Defaulted to the legacy | Re-derive from the product goal |
| Showing all problems at once | Tiered plans by information volume | Tier by help, speed, scope, proof |
| Slow, blind debugging | Long loops without a feedback loop | Make failures surface fast, fix the class |
| Defaults that ignore the project's own rules | Built before reading the brief | Check the project's standing rules first |

## 6. Persuasion through truth

Convert and retain by being right about the customer's business, never by pressure. Every persuasion lever must be honest, reversible and provable.

- **Allowed:** the customer's own real numbers, a clear next step, a fair default, a visible guarantee, real proof, a reminder before a renewal, a cancel button that works in one click.
- **Banned dark patterns:** fake timers or scarcity, fabricated reviews, logos, counts, certifications or press, confirmshaming, hard cancel, pre-checked add-ons, hidden prices, forced continuity without a reminder. Each has an ethical replacement in `references/dark-patterns.md`.
- **No data, no claim.** With no customers there are no testimonials. Show the product's own output, or a clearly labelled "Example workspace".
- **Every conversion change ships as an experiment:** hypothesis, metric (a named analytics event), readout date, ICE score. Template in `references/funnel-map.md`.
- Consent banners, analytics and legal pages follow the project's own decision; honour DNT and GPC signals and keep the legal pages truthful.

## 7. Consistency inside, variety outside

- **Inside the product (dashboard, settings, admin, docs):** one page template and one set of patterns, so a user learns once. "Every page must be unique" does not apply to product screens.
- **Marketing pages only:** variety of layout and mockups is welcome, as long as each page keeps one thesis and one CTA.

## 8. Page count is never a goal

A page earns its place by a job: it answers one question, moves one stage of the funnel, or resolves one support need. "100+ pages" is not a target. Merge or remove a page without a job. Never create pages (Investor Relations, Press, Certifications) for a company that has none of what they would claim.

## 9. Where the depth lives (load at the step named)

- `references/conversion-psychology.md`: principles mapped to SaaS surfaces. Load when designing or reviewing a surface that must convert or retain.
- `references/funnel-map.md`: stages, KPIs, events and the experiment template. Load when planning a change meant to move a metric.
- `references/dark-patterns.md`: banned list with replacements. Load before writing any pricing, trial, cancel, social proof or urgency copy.
- Older prompts that conflict with these rules: the canonical values in `modules/line-balance/GUIDE.md` win.
