# Dark patterns and their ethical replacements

Load before writing pricing, trial, checkout, cancel, urgency, social proof or consent copy. Rule: if a lever works only because the customer does not notice it, it is banned. Replace it with a lever that survives the customer reading it out loud.

Legal and brand reasons:
- **FTC click-to-cancel (Negative Option Rule, USA):** cancelling must be as easy as signing up, with the same channel. Deceptive cancel flows and unclear recurring terms are enforced under FTC Act section 5 and ROSCA.
- **EU Digital Services Act (Art. 25) and consumer law:** interfaces must not deceive or manipulate. Fake urgency, hidden costs and obstructed withdrawal are targeted.
- **Brand:** a product that sells truth about a business loses its whole claim on one false number. A false number anywhere makes every true number suspect.

## The list

| Banned | What it looks like | Ethical replacement | Why |
|---|---|---|---|
| Fake timer or scarcity | Countdown that resets, "3 spots left" with no cap | A real deadline only when it exists (trial end date from the account, a dated price change). Show the date, not a ticking clock | FTC, DSA, brand |
| Fabricated reviews | Invented quotes, star ratings, "loved by teams" | No customers yet: show the product's own output on a real site, or an "Example workspace" label. Real quotes only with written permission | FTC endorsement rules, brand |
| Fabricated logos, counts, press, certifications | "Trusted by 10,000", logo wall, "SOC 2" without audit | State only counts the database returns (live query, with date). Certifications only after issued, linked to the report | FTC, brand |
| Confirmshaming | "No thanks, I hate growing" | Neutral decline: "Not now". Same weight as the accept button | DSA |
| Hard cancel | Cancel hidden, needs a call or chat, five screens | Cancel in Settings > Billing, one click plus one confirm, same session. Offer pause or downgrade as an option beside it, never in front of it | FTC click-to-cancel |
| Pre-checked add-ons | Seat packs or upsells ticked at checkout | Unchecked by default, price shown beside it, total updates live | DSA, consumer law |
| Hidden prices | "Contact us", fees at the last step | Full price, currency, billing period and tax note on the plan card and at checkout. Total before the pay button | FTC junk fees, DSA |
| Forced continuity without reminder | Trial converts silently | Trial end date shown in app; email 3 days and 1 day before the first charge with a cancel link; receipt after charge | ROSCA, FTC |
| Roach motel (easy in, hard out) | Signup 1 click, data export impossible | Export and delete in Settings, self-serve | GDPR, DSA |
| Nagging and misdirection | Upgrade modal on every page load, grey "close" | At most one upgrade moment per session, tied to a real limit just hit, visible close | DSA, focus law |
| Trick questions | Double negatives in email opt-ins | One plain checkbox, unchecked, plain words | GDPR |
| False personalisation | "Only 2 left for you", invented "other members like you" | Personalise from the member's real stage and data, say what it is based on | brand |
| Fake progress | Progress bar that jumps to 80% for nothing | Progress that moves only on measured events (see Evidence, not ticks) | brand |

## Scenario rules (used by selftest)

- "Add testimonials, we have no customers": do not invent them. Show the product's own output, or label it "Example workspace". Add a real-quote slot that renders nothing until a real, permitted quote exists.
- "Add a countdown to the offer": only if the deadline is a real date stored in the account or the plan. Show the date.
- "Make cancel harder to cut churn": no. Add pause, downgrade and a one-question exit survey beside a working Cancel.
- "Pre-select the annual plan": a default is allowed when both prices and the saving are visible and the choice is one click to change. Pre-checking a paid add-on is not.

## Review checklist

- Every number on the page comes from data we can show, with a date.
- Leaving is as easy as arriving.
- Total price shows before the pay button.
- Copy that survives being read aloud, mechanism included.
- The change has an experiment record: hypothesis, metric event, readout date, ICE.
