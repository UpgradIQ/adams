# Example Execution — Project Management Software Comparisons

**Niche:** Project management (PM) software comparisons
**Mode:** Data-Connected (using example-keyword-sheet.csv)
**Monetization model:** Affiliate (SaaS referral programs)
**Target country:** US
**Preferred stack:** Astro
**DA assumption:** New domain (DA 0)
**Content capacity:** 30 pages per week

---

## Step 1 — Intake Summary

All required inputs are present. No default assumptions needed.

Operating in Data-Connected mode. CSV contains 20 seed keywords across 7 clusters.

---

## Step 2 — Keyword Clusters

### Cluster A — Tool Comparisons (Broad)
- Intent: Commercial
- Keywords: best project management software, best pm tool for startups,
  project management software for small business
- Volume: 21,600/month combined
- Page potential: 40–60 pages (tool + use-case variants)

### Cluster B — Direct Head-to-Head Comparisons
- Intent: Commercial
- Keywords: asana vs monday.com, asana vs trello, clickup vs asana
- Volume: 13,800/month combined
- Page potential: 20–50 pages (all tool pair combinations from a set of 15 tools)

### Cluster C — Pricing Pages
- Intent: Transactional
- Keywords: monday.com pricing, asana pricing, clickup pricing
- Volume: 28,200/month combined
- Page potential: 15–25 pages (one per major tool)

### Cluster D — Free Tools
- Intent: Transactional
- Keywords: free project management software, free task management app
- Volume: 12,000/month combined
- Page potential: 5–10 pages (filtered list + profiles)

### Cluster E — Alternatives
- Intent: Commercial
- Keywords: asana alternatives, monday.com alternatives, trello alternatives
- Volume: 14,400/month combined
- Page potential: 15–25 pages (one per major tool)

### Cluster F — Industry-Specific
- Intent: Commercial
- Keywords: pm software for construction, pm software for healthcare,
  pm tools for agencies
- Volume: 3,900/month combined
- Page potential: 30–80 pages (industry × tool combinations)

### Cluster G — How-To Guides
- Intent: Informational
- Keywords: how to manage a project, how to use asana, methodology comparison
- Volume: 9,800/month combined
- Page potential: 20–40 pages (supporting content hub)

---

## Step 3 — Intent Mapping

| Cluster | Intent | Static Site Fit | Action |
|---|---|---|---|
| A — Tool Comparisons | Commercial | Excellent | Build as core index pages |
| B — Head-to-Head | Commercial | Excellent | Build as comparison template |
| C — Pricing | Transactional | Good | Build as pricing sub-pages per tool |
| D — Free Tools | Transactional | Good | Build as filtered list |
| E — Alternatives | Commercial | Excellent | Build as alternatives template |
| F — Industry-Specific | Commercial | Excellent | Build as faceted filter pages |
| G — How-To Guides | Informational | Good | Build as authority hub supporting content |

No mixed-intent clusters detected. No splits required.

---

## Step 4 — Opportunity Scoring

Three project options evaluated:

### Option A — Full Comparison Database (all clusters)
Covers all 7 clusters. Broad positioning.

### Option B — Comparison + Alternatives Focus
Clusters A, B, E, F only. Commercial intent only. Tighter focus.

### Option C — Industry-Specific Directory
Cluster F only. Narrower scope. Lower competition.

| Project | Demand | Feasibility | Focus | Monetization | Scalability | Maintenance | Uniqueness | Speed | Total |
|---|---|---|---|---|---|---|---|---|---|
| A — Full Comparison Database | 4 | 2 | 3 | 5 | 5 | 4 | 3 | 3 | 29 |
| B — Comparison + Alternatives | 4 | 3 | 4 | 5 | 4 | 4 | 4 | 4 | 32 |
| C — Industry-Specific Directory | 3 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | 33 |

**Score notes:**

- Option A: Strong demand but DA 0 makes ranking against G2/Capterra near-impossible
  in broad terms. Feasibility score adjusted from 3 to 2 for DA 0.
- Option B: Better topical focus. Commercial pages accessible with long-tail targeting.
- Option C: Highest feasibility for new domain. Industry filters create natural
  differentiation. Fastest to MVP.

---

## Step 5 — Project Selection

**Selected: Option C — Industry-Specific PM Software Directory**

**Why:**
- Topical focus score is highest (5/5). Every page reinforces the same authority signal.
- Feasibility is highest for a DA 0 domain. Industry-specific queries have weak SERP
  competition compared to broad PM tool searches.
- Data schema is well-defined and stable. Maintenance burden is low.
- Programmatic scalability is high: industry x tool combinations produce 60–120 pages
  from a single schema.
- Speed to MVP is fast: 15–20 pages can go live in Week 1.

**Runner-up: Option B — Comparison + Alternatives**
Prefer this when the domain reaches DA 15+ and can target broader commercial terms.
Consider as Phase 2 expansion.

**Risk flags:**
- Thin content risk: Industry-specific pages must have genuine unique content per
  industry, not just a swapped label.
- Data freshness: SaaS pricing and features change. Plan for quarterly data review.
- Differentiation: Must include industry-specific criteria scoring (not generic star ratings).

---

## Step 6 — Site Architecture

### URL Structure

```
/                                       → Homepage
/industries/                            → All industries index
/industries/[industry-slug]/            → Industry index (e.g., /industries/construction/)
/tools/                                 → All tools index
/tools/[tool-slug]/                     → Tool profile
/tools/[tool-slug]/[industry-slug]/     → Tool profile for specific industry
/compare/[tool-a]-vs-[tool-b]/          → Head-to-head (Phase 2)
/free/                                  → Free tools filtered list
/about/                                 → About page
```

### Page Hierarchy

```
Level 0: Homepage (1 page)
Level 1: Industry indexes (8–12 pages), Tools index (1 page)
Level 2: Industry tool lists (8–12 pages), Tool profiles (15–20 pages)
Level 3: Tool × Industry pages (60–120 pages)
```

### Page Count Estimate

| Page Type | Count | Method |
|---|---|---|
| Homepage | 1 | Manual |
| Industry indexes | 10 | Template |
| Tools index | 1 | Template |
| Tool profiles | 20 | Programmatic |
| Tool × Industry pages | 80 | Programmatic |
| Free tools list | 1 | Template |
| About | 1 | Manual |
| **Total** | **114** | |

---

## Step 7 — Template and Page Model

### Page Type: Tool × Industry Profile

**URL:** `/tools/[tool-slug]/[industry-slug]/`
**Purpose:** Helps professionals in a specific industry evaluate whether a given PM tool
fits their workflow.

**Required data fields:**

| Field | Type | Source |
|---|---|---|
| tool_name | string | Manual dataset |
| industry | string | Manual dataset |
| industry_use_case_score | number (1–10) | Editorial review |
| pricing_from | number (USD/month) | Tool pricing page |
| free_plan | boolean | Tool pricing page |
| key_features_for_industry | array (3–5 items) | Editorial review |
| limitations_for_industry | array (1–3 items) | Editorial review |
| best_for_team_size | string | Editorial review |
| integrations_relevant_to_industry | array | Tool documentation |
| last_reviewed | date | Editorial |

**Page sections:**

1. Summary verdict (2–3 sentences, industry-specific recommendation)
2. Industry fit score + breakdown table
3. Key features for this industry (3–5 items with descriptions)
4. Limitations for this industry (1–3 items)
5. Pricing for this use case
6. Best alternatives in this industry (links to 3 competitor tool × industry pages)
7. Bottom line (1 sentence recommendation)

**Title tag formula:**
`[Tool Name] for [Industry]: Honest Review [Year] | [Site Name]`

**Meta description formula:**
`Is [Tool] right for [Industry] teams? See features, pricing, limitations, and alternatives. [X]-minute review.`

---

## Step 8 — SEO Specification

### Metadata Rules

**Tool × Industry pages:**
- Title: `[Tool] for [Industry]: Review [Year] | [Brand]` (max 65 characters)
- Description: `See if [Tool] fits [Industry] teams. Features, pricing, and [Industry] alternatives covered.` (max 155 characters)

**Industry index pages:**
- Title: `Best Project Management Software for [Industry] [Year] | [Brand]`
- Description: `Compare the top PM tools for [Industry]. Filter by price, features, and team size.`

### Schema Markup Plan

| Page Type | Schema Type | Key Fields |
|---|---|---|
| Tool profile | SoftwareApplication | name, applicationCategory, offers, aggregateRating |
| Tool × Industry | Review + SoftwareApplication | itemReviewed, reviewRating, author, datePublished |
| Industry index | ItemList | itemListElement (each tool in list) |
| Homepage | WebSite + Organization | name, url, description |

### Canonical Rules

- Each page has a self-referencing canonical.
- Tool × Industry pages canonicalize to themselves (not to the parent tool profile).
- Filter combinations with fewer than 5 results: `noindex, follow`.

### Sitemap Priority

| Page Type | Priority | Change Frequency |
|---|---|---|
| Homepage | 1.0 | Monthly |
| Industry indexes | 0.9 | Monthly |
| Tool × Industry pages | 0.8 | Quarterly |
| Tool profiles | 0.7 | Quarterly |
| Supporting pages | 0.5 | Yearly |

---

## Step 9 — Build Plan

### Stack Recommendation

**Astro** with Markdown/MDX content layer and JSON data files.

Rationale:
- Zero JS by default = fast page loads.
- Content collections API supports structured data for programmatic generation.
- No lock-in: can be deployed to Netlify, Vercel, Cloudflare Pages, or any CDN.
- Clean separation of data (JSON) and templates (Astro components).

### Data Pipeline

```
[Manual dataset: tools.json]
        ↓
[Manual dataset: industries.json]
        ↓
[Build script: generate tool × industry page routes]
        ↓
[Astro content collections → static HTML pages]
        ↓
[Deploy to Cloudflare Pages]
```

### Sprint Plan

**Week 1 — Foundation**
- Configure Astro project and deploy pipeline.
- Build tools.json and industries.json datasets (15 tools, 10 industries).
- Build homepage and all-industries index template.
- Deploy 20 tool × industry pages.

**Week 2 — Core Pages**
- Build tool profile template.
- Build industry index template.
- Complete all tool × industry pages (target: 60 pages live).

**Week 3 — SEO and Linking**
- Implement schema markup on all page types.
- Implement internal linking logic.
- Configure sitemap.xml and robots.txt.
- Submit to Google Search Console.

**Week 4 — Content Quality Pass**
- Review 100% of generated pages for thin content.
- Add editorial summary sections to all industry index pages.
- Add FAQ sections to top 20 pages by search volume.

**MVP definition:** 60 tool × industry pages + 10 industry indexes + 15 tool profiles.
Live by end of Week 2.

### Risk Flags

| Risk | Severity | Mitigation |
|---|---|---|
| Thin industry × tool pages | High | Require 5 unique editorial fields per page. No page goes live without review. |
| DA 0 slow ranking | Medium | Target long-tail industry-specific queries first. Build topical depth before breadth. |
| SaaS pricing changes | Medium | Quarterly data review cycle. Include "last reviewed" date on every page. |
| Low differentiation from G2 / Capterra | High | G2 and Capterra use generic star ratings. Differentiate with industry-specific scoring criteria. |

---

## Step 10 — KPI Measurement Plan

**North Star Metric:** Organic sessions per month

**6-month targets (new domain):**

| Month | Indexed Pages | Organic Sessions | Average Position |
|---|---|---|---|
| 1 | 60 | 100–300 | 30–50 |
| 2 | 100 | 300–800 | 25–40 |
| 3 | 114 | 800–2,000 | 20–35 |
| 6 | 114 | 3,000–8,000 | 10–25 |

**Leading indicators to watch weekly:**
1. Pages indexed in Search Console vs. pages submitted.
2. Average click-through rate on Tool × Industry pages.
3. Top ranking pages by cluster — confirm industry-specific pages rank before broad pages.

**Pruning policy:** Pages with zero impressions after 90 days are reviewed.
If no search demand exists for the combination, the page is consolidated into the
parent industry index (301 redirect to industry page).
