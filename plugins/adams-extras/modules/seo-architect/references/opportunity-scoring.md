# Opportunity Scoring Framework

## Overview

Score each static project idea on 8 factors. Each factor scores 1–5.
Maximum total: 40. Minimum viable score: 20.

Projects below 20 are flagged as high-risk. Do not recommend them as primary build targets.

---

## Scoring Factors

### Factor 1 — Search Demand (1–5)

Measures whether enough people search for this topic to make the project worthwhile.

| Score | Criteria |
|---|---|
| 5 | Core cluster has 10,000+ monthly searches. Multiple secondary clusters available. |
| 4 | Core cluster has 2,000–10,000 monthly searches. Solid secondary demand. |
| 3 | Core cluster has 500–2,000 monthly searches. Niche but consistent. |
| 2 | Core cluster has under 500 monthly searches. Limited scale potential. |
| 1 | No reliable data. Demand is speculative. |

**Data-Light adjustment:** If no volume data is available, score based on the number of distinct
keyword modifiers that can be constructed from the seed keywords.

- 6+ modifiers = score 3
- 10+ modifiers = score 4
- 20+ modifiers = score 5

---

### Factor 2 — Ranking Feasibility (1–5)

Measures how realistic it is for a new or low-DA domain to rank.

| Score | Criteria |
|---|---|
| 5 | Top 10 SERPs contain DA < 30 sites. Multiple long-tail gaps visible. |
| 4 | Top 10 SERPs have a mix of high and low DA. Long-tail terms are accessible. |
| 3 | Top 10 SERPs dominated by DA 40–60. Requires strong topical authority. |
| 2 | Top 10 SERPs dominated by DA 60+. Difficult without established presence. |
| 1 | SERPs dominated by major brands or aggregators. Near-impossible for new entrant. |

**Data-Light adjustment:** Use niche characteristics as a proxy.

- Emerging or highly specific niche = score 4
- Established niche with known brands = score 2–3
- Dominated by Amazon, Wikipedia, G2, Capterra = score 1–2

---

### Factor 3 — Topical Focus (1–5)

Measures whether the project has a coherent, defensible topical scope.

| Score | Criteria |
|---|---|
| 5 | Single, clearly bounded topic. All pages reinforce the same authority signal. |
| 4 | One primary topic with 1–2 closely related sub-topics. |
| 3 | 2–3 topic areas. Some dilution risk. |
| 2 | Broad or loosely connected topics. Hard to build topical authority. |
| 1 | No coherent topical scope. Will not rank well by design. |

---

### Factor 4 — Monetization Potential (1–5)

Measures how naturally the project converts traffic into revenue.

| Score | Criteria |
|---|---|
| 5 | Direct affiliate/lead-gen fit. High buyer intent. Revenue model is proven in this niche. |
| 4 | Clear monetization path. Moderate buyer intent. Requires some funnel work. |
| 3 | Indirect monetization (ads, sponsorship). Revenue is possible but lower per-visitor. |
| 2 | Weak monetization fit. Traffic is informational with low commercial value. |
| 1 | No viable monetization path identified. |

---

### Factor 5 — Programmatic Scalability (1–5)

Measures how well the project scales through programmatic page generation.

| Score | Criteria |
|---|---|
| 5 | 100+ pages can be generated from a single data schema. Clear template structure. |
| 4 | 50–100 pages. Moderate templating required. |
| 3 | 20–50 pages. Some manual content required at scale. |
| 2 | Under 20 pages. Limited programmatic leverage. |
| 1 | Every page requires unique manual production. Not suitable for programmatic approach. |

---

### Factor 6 — Maintenance Burden (1–5)

Measures how much ongoing effort the site requires after launch.
**Higher score = lower burden (better).**

| Score | Criteria |
|---|---|
| 5 | Static data. Pages rarely need updating. Near-zero maintenance. |
| 4 | Data refreshes quarterly or less. Simple update process. |
| 3 | Monthly data refreshes required. Some automation needed. |
| 2 | Frequent updates (weekly). Requires ongoing editorial or data work. |
| 1 | Real-time or near-real-time data dependency. High maintenance. |

---

### Factor 7 — Content Uniqueness Potential (1–5)

Measures whether each programmatically generated page can offer genuine unique value.

| Score | Criteria |
|---|---|
| 5 | Each page has a unique data combination that no competitor currently offers. |
| 4 | Pages are differentiated but competitors have partial coverage. |
| 3 | Pages are differentiated by structure but content is similar to competitors. |
| 2 | High duplication risk. Pages look similar to existing SERP results. |
| 1 | Thin content risk is severe. Pages would offer nothing not already available. |

---

### Factor 8 — Speed to MVP (1–5)

Measures how quickly a working version can be live.
**Higher score = faster to MVP.**

| Score | Criteria |
|---|---|
| 5 | MVP live in under 1 week. Simple data + simple template. |
| 4 | MVP live in 1–2 weeks. Moderate complexity. |
| 3 | MVP live in 2–4 weeks. Requires data collection or custom components. |
| 2 | MVP requires 4–8 weeks. Complex data pipeline or content production. |
| 1 | MVP requires more than 2 months. Not suitable for fast validation. |

---

## Scoring Table Template

```markdown
| Project Idea | Demand | Feasibility | Focus | Monetization | Scalability | Maintenance | Uniqueness | Speed | Total |
|---|---|---|---|---|---|---|---|---|---|
| [Project A]  |   /5   |    /5       |  /5   |     /5       |     /5      |     /5      |    /5      |  /5   |  /40  |
| [Project B]  |   /5   |    /5       |  /5   |     /5       |     /5      |     /5      |    /5      |  /5   |  /40  |
```

---

## Score Interpretation

| Total Score | Interpretation |
|---|---|
| 35–40 | Strong opportunity. Build first. |
| 28–34 | Good opportunity. Worth building after top pick. |
| 20–27 | Marginal opportunity. Proceed only with mitigations. |
| Below 20 | High risk. Flag and do not recommend as primary target. |

---

## Adjustments for DA Level

Apply these modifiers to Ranking Feasibility before calculating totals:

| DA Level | Modifier |
|---|---|
| New (DA 0) | -1 to Feasibility if score was 4 or 5 |
| Low (DA 1–20) | No adjustment |
| Medium (DA 20–40) | +1 to Feasibility if score was 2 or 3 |
| High (DA 40+) | +1 to Feasibility (cap at 5) |
