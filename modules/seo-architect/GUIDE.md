# Programmatic SEO Static Project Architect

## What This Skill Does

This skill moves a project from a raw keyword idea or niche to a fully specified,
implementation-ready static site plan. It produces structured outputs — not generic advice.

It operates in two modes:

| Mode | When to Use | Data Available |
|---|---|---|
| **Data-Connected** | Keyword exports, volume data, or competitor data available | CSV, Ahrefs/Semrush exports, SimilarWeb data |
| **Data-Light** | Only seed keywords, a niche description, or basic inputs | User-supplied context only |

In Data-Light mode, use structural reasoning, search intent logic, and explicit assumptions
to produce outputs that are still actionable.

---

## Input Schema

### Required Inputs

| Input | Description | Example |
|---|---|---|
| `niche` | Market category or topic space | "project management software comparisons" |
| `seed_keywords` | 3–10 starting keyword phrases | "best PM tools, PM software for startups" |
| `monetization_model` | How the site will earn | affiliate, lead gen, SaaS, ads, digital product |
| `target_country` | Primary search market | US, UAE, UK, Global |

### Optional Inputs

| Input | Description |
|---|---|
| `keyword_csv` | Exported keyword data with volume and difficulty |
| `competitor_domains` | Up to 5 competitor URLs for gap analysis |
| `preferred_stack` | Next.js, Astro, Eleventy, Hugo, plain HTML |
| `domain_authority_assumption` | New (DA 0), Low (DA 1–20), Medium (DA 20–40) |
| `content_capacity` | Pages producible per week (e.g., 10, 50, 500) |
| `language` | Target language (default: English) |
| `budget_assumption` | Hosting + tooling budget per month |

### Default Assumptions (when optional inputs are absent)

- Stack: Astro (static-first, framework-agnostic content layer)
- DA: New domain (DA 0), targeting long-tail keywords
- Content capacity: 20–50 pages per sprint
- Language: English
- Budget: Under USD 50/month (static hosting + minimal tooling)

---

## Operating Workflow

Follow these steps in sequence. Document assumptions at each step.

### Step 1 — Intake

1. Parse all inputs supplied by the user.
2. Identify missing required inputs. If any are missing, fill with defaults and state
   the assumption clearly.
3. Confirm operating mode: Data-Connected or Data-Light.
4. State the niche scope clearly before proceeding.

### Step 2 — Keyword Clustering

**If Data-Connected:**
- Group keywords by shared modifier patterns (e.g., "best X for Y", "X vs Y", "X pricing").
- Remove branded, navigational, and irrelevant keywords.
- Tag each cluster with a primary intent (see Step 3).

**If Data-Light:**
- Generate likely keyword patterns from the seed keywords using intent logic.
- Produce 4–8 keyword clusters using the modifier matrix below.

**Modifier Matrix (use to expand seed keywords):**

| Pattern | Example | Typical Intent |
|---|---|---|
| `best [X] for [Y]` | best CRM for freelancers | Commercial |
| `[X] vs [Y]` | Notion vs Asana | Commercial |
| `[X] pricing` | Monday.com pricing | Commercial/Transactional |
| `how to [do X]` | how to set up a kanban board | Informational |
| `[X] alternatives` | Asana alternatives | Commercial |
| `[X] review` | ClickUp review | Commercial |
| `free [X]` | free project management tool | Transactional |
| `[X] for [industry]` | PM software for construction | Commercial |

Read `references/opportunity-scoring.md` before scoring in Step 4.

### Step 3 — Intent Mapping

Assign each keyword cluster one of four intents:

| Intent | Signal | Static Site Fit |
|---|---|---|
| **Informational** | how, what, why, guide, tips | Good — content pages |
| **Commercial** | best, vs, review, alternative, top | Excellent — comparison pages |
| **Transactional** | buy, get, free, download, pricing | Moderate — landing pages |
| **Navigational** | brand name, login | Poor — skip |

Flag any clusters that mix intent types. Split mixed-intent clusters before scoring.

### Step 4 — Opportunity Scoring

Score each project idea using the 8-factor framework in `references/opportunity-scoring.md`.

Produce a scored shortlist table. Minimum columns:

```
| Project | Demand | Feasibility | Focus | Monetization | Scalability | Maintenance | Uniqueness | Speed | Total |
```

Total = sum of scores (max 40). Projects scoring below 20 should be flagged or dropped.

### Step 5 — Project Selection

Select the top-scoring project. State:
1. Why this project scores highest.
2. What assumptions drive the score.
3. What risks exist (thin content, duplication, weak differentiation).
4. What the runner-up is and when it would be preferable.

Read `references/site-patterns.md` before designing architecture in Step 6.

### Step 6 — Site Architecture Design

Produce:
1. A site map with page types and hierarchy.
2. An internal linking logic diagram (text-based, Markdown).
3. A URL structure specification.
4. A content taxonomy (categories, tags, facets if applicable).

### Step 7 — Template and Page Model Design

Define:
1. The programmatic page types required.
2. The data schema for each page type (fields, sources, rendering logic).
3. The template layout for each page type.
4. Rules for page differentiation (what makes each page unique).

Read `references/output-templates.md` for exact output format specifications.

### Step 8 — SEO Specification

Produce:
1. Metadata rules (title tag formula, meta description formula).
2. Schema markup plan per page type.
3. Canonical rules.
4. Crawl priority rules (robots.txt logic, sitemap priority).

Read `references/seo-guardrails.md` before drafting SEO specs.

### Step 9 — Build Plan

Produce:
1. Stack recommendation with rationale.
2. Data pipeline design (data source → transformation → page generation).
3. Sprint plan (Week 1 through launch).
4. MVP definition: minimum pages to go live.
5. Risk flags.

### Step 10 — Output Packaging

Produce all outputs using the exact templates in `references/output-templates.md`.

Collect into a single structured response or a set of clearly labelled Markdown files.

---

## Reference Files

| File | When to Read |
|---|---|
| `references/opportunity-scoring.md` | Before Step 4 (scoring) |
| `references/site-patterns.md` | Before Step 6 (architecture) |
| `references/seo-guardrails.md` | Before Step 8 (SEO spec) |
| `references/output-templates.md` | Before Step 10 (output packaging) |

---

## Design Principles

1. **Modular outputs** — each section can be used independently.
2. **No lock-in** — architecture decisions must be portable across static site generators.
3. **No thin content** — every page type must have a clear differentiation rule.
4. **Low maintenance** — prefer data-driven generation over manual content at scale.
5. **Durable value** — target stable informational demand, not trend spikes.
6. **Simple English** — output must be readable by non-native English speakers.
7. **Explicit assumptions** — state every assumption. Never leave logic implicit.
