# Conversion psychology for a SaaS, mapped to surfaces

Load when designing or reviewing a surface that must convert or retain. Every principle here is used honestly: it shapes the order and framing of true information, never the truth. Banned levers are in `dark-patterns.md`. Never invent a figure: use the customer's own data, or label it "Example workspace". Surface names below are examples from a growth-analytics SaaS (Score, Diagnosis, Monitor, Competitors, Roadmap, Experiments, Results, Reports, Advisor, a free site test and a time-limited paid trial). Map them to your own product's equivalents, and read plan names and limits from your plan table, never from this file.

## Surface map: which principles to check

| Surface | Principles |
|---|---|
| Free test (site test on the homepage) | time to value, reciprocity, Fogg B=MAP, Hick, IKEA |
| Setup and onboarding | commitment ladder, endowed progress, goal gradient, personalisation, Fogg |
| First value (first Score or Diagnosis) | time to value, peak-end, IKEA, Hook (reward) |
| Dashboard home | Zeigarnik with the focus law, Hick, goal gradient, Hook (trigger) |
| Upgrade moments | paywall at the moment of value, loss aversion with real numbers, objection handling |
| Pricing page | anchoring, decoy, default, risk reversal, real social proof, objection handling |
| Trial end | loss aversion (own numbers), endowed progress, risk reversal, peak-end |
| Cancel flow | peak-end, objection handling, risk reversal (no hard cancel) |
| Lifecycle emails | Hook (trigger), Zeigarnik, reciprocity, personalisation |
| Monthly value summary | loss aversion (own numbers), peak-end, Hook (investment), real social proof |

## The principles

Format: what it is, where it applies, Do, Don't.

### 1. Time to value and the aha moment
- **What:** the minutes from first visit to the first moment the customer sees something true and useful about their own business.
- **Where:** free test, first Score, first Diagnosis.
- **Do:** run the real check on their site before asking for an account; show the result first, the signup second. Measure time to first value as a funnel event.
- **Don't:** put a tour, a long form or a survey before the first result.

### 2. Fogg behaviour model (B = Motivation, Ability, Prompt)
- **What:** a behaviour happens only when motivation, ability and a prompt meet at the same moment.
- **Where:** every CTA, every setup step, every connector.
- **Do:** when a step is skipped, lower the effort first (prefill, one field, one click) before adding motivation copy. Place the prompt where motivation peaks (right after a result).
- **Don't:** add urgency to a step that is hard; make it easy instead.

### 3. Reciprocity
- **What:** people return value they received first.
- **Where:** free site test, Example workspace, a useful finding before signup.
- **Do:** give a real finding for free, specific to their site, with the next step named.
- **Don't:** gate the finding behind a signup wall and then call it free; do not ask for a favour (review, referral) before value is delivered.

### 4. Commitment ladder
- **What:** small agreed steps make the next step natural.
- **Where:** visitor > free test > signup > connect first source > first Experiment > paid.
- **Do:** one rung per screen, each rung gives something back, and the rung after it is visible.
- **Don't:** ask for a card, a team invite and three connectors in the same session.

### 5. Loss aversion with the customer's own real numbers
- **What:** losing something feels bigger than gaining the same thing.
- **Where:** trial end, downgrade, pause, cancel.
- **Do:** show what the customer built and would lose, with their real data and dates: "Your Roadmap has 6 open items, your Monitor has 30 days of history" only when the database says so.
- **Don't:** threaten ("you will fall behind"), invent a cost, or use industry averages as if they were theirs.

### 6. Endowed progress
- **What:** people finish what already looks started.
- **Where:** setup checklist, first-week plan.
- **Do:** start the checklist at a truthful state: account created and site tested are real, already done steps. Show them done.
- **Don't:** pre-fill steps that were not done, or move a progress bar on anything but a measured event.

### 7. Goal gradient
- **What:** effort accelerates as the goal gets close.
- **Where:** setup, Roadmap, Score improvement.
- **Do:** show distance to the next real milestone ("2 of 3 sources connected"), and make the last step the smallest.
- **Don't:** show a long progress bar with fake early jumps, or milestones the customer cannot reach.

### 8. Zeigarnik effect (with the focus law)
- **What:** unfinished tasks stay in mind more than finished ones.
- **Where:** dashboard home, lifecycle emails, Roadmap.
- **Do:** surface the one unfinished item that matters, maximum 3 per surface, in order. Resume where they stopped.
- **Don't:** list every open problem; a wall of open loops creates anxiety and churn, and breaks the focus law.

### 9. Hick's law
- **What:** decision time grows with the number of choices.
- **Where:** dashboard main area, pricing, settings, navigation.
- **Do:** one primary action per screen, at most 3 next items, 3 plans, depth behind a click.
- **Don't:** equal-weight tiles for every capability, or more than 4 tabs.

### 10. IKEA effect
- **What:** people value what they helped build.
- **Where:** setup (their goals, competitors, priorities), Experiments, Reports.
- **Do:** let them pick their own goal, name an Experiment, choose the competitors to track, then reuse those choices everywhere.
- **Don't:** auto-fill their strategy for them, which removes the investment that makes leaving costly in a healthy way.

### 11. Peak-end rule
- **What:** an experience is remembered by its peak and its end.
- **Where:** first result, success states, trial end, cancel, monthly summary.
- **Do:** make the success state a small, real celebration with the next step; make the end of a trial and of a cancel respectful, with data export offered.
- **Don't:** end on a guilt screen, an upsell modal or an error with no fix.

### 12. Anchoring, decoy and default on pricing
- **What:** the first number seen sets the frame; a middle option can make a target plan clearer; a default is chosen most often.
- **Where:** pricing page, upgrade dialog.
- **Do:** show the top plan first or the annual saving computed from the real prices; make the recommended plan the visible default with a plain reason; compare plans on what changes for the customer.
- **Don't:** show a fake "was" price, build a plan nobody should buy, pre-check paid add-ons or hide the monthly price.

### 13. Risk reversal
- **What:** removing the fear of a bad purchase raises the decision rate.
- **Where:** pricing page, trial start, checkout, cancel.
- **Do:** state the real terms in plain words: 7-day Pro trial, the date the first charge happens, reminder before it, cancel in one click, refund terms exactly as they are.
- **Don't:** promise a guarantee the business does not honour or bury the terms.

### 14. Real social proof only
- **What:** people follow the evidence of others like them.
- **Where:** homepage, pricing, trial end, monthly summary.
- **Do:** use real counts from the database with an as-of date, real permitted quotes, or the product's own output. With none, show an "Example workspace" labelled as such.
- **Don't:** invent logos, quotes, counts, ratings or certifications, or show an example without the label.

### 15. Paywall at the moment of value, never a wall
- **What:** ask for money when the customer has just felt the value of the thing they want next.
- **Where:** a Diagnosis finding that Monitor would track, a Competitors limit, an Advisor question beyond the plan.
- **Do:** show the real result at the free level, name the exact limit hit, show what the next plan adds, one dismissible prompt per session.
- **Don't:** block the dashboard, blur the whole result, or interrupt a task in progress.

### 16. Hook model (trigger, action, variable reward, investment)
- **What:** a habit forms when an external trigger leads to an easy action, a rewarding and varying outcome, and an investment that improves the next round.
- **Where:** weekly Score change email, Monitor alerts, Results, Reports.
- **Do:** trigger on a real change (Score moved, competitor changed, Experiment finished); reward with a true new finding; investment is their saved goals, history and notes.
- **Don't:** send a trigger with nothing new in it, or invent a variable reward (fake streaks, random badges).

### 17. Personalisation by stage and role
- **What:** the same product is framed differently for a founder at idea stage and a head of growth at scale.
- **Where:** onboarding question, dashboard first Action, emails.
- **Do:** ask stage and role once, in setup; change the first Roadmap items and the examples, say why ("because you are pre-revenue").
- **Don't:** segment into dozens of paths, or personalise on guessed data.

### 18. Objection handling
- **What:** each hesitation has a known cause; answer it where it appears.
- **Where:** pricing page, trial start, upgrade dialog, cancel flow.
- **Do:** list the real objections (price, setup effort, data safety, lock-in, "will it work for my business") and answer each next to the CTA with a link to the article in docs.
- **Don't:** hide the objection or answer with adjectives; use a fact, a number we hold, or a clear term.

## Copy rules that apply to all of them

Sentence case, no em dash, Latin digits, outcome-based button labels ("Run my site test", "Connect Search Console"), never "Submit", "Click here", "Learn more" with no object. Short text on one line at 375 and 1280.
