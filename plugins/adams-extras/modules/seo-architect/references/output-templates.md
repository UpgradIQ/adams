# Output Templates

## How to Use This File

Copy each template and fill in the bracketed fields. Do not omit sections.
Add an "Assumptions" block at the top of any template where inputs were absent.

---

## Template 1 — Opportunity Shortlist

```markdown
# Keyword Opportunity Shortlist

**Niche:** [niche]
**Date:** [date]
**Mode:** [Data-Connected / Data-Light]

## Assumptions
- [List any assumptions made due to missing data]

## Keyword Clusters

### Cluster 1 — [Cluster Name]
- **Intent:** [Commercial / Informational / Transactional]
- **Seed keywords:** [keyword 1, keyword 2, keyword 3]
- **Estimated monthly volume:** [number or range]
- **Keyword patterns:** [modifier patterns identified]
- **Page count potential:** [estimated number of addressable pages]

### Cluster 2 — [Cluster Name]
[repeat structure]

## Summary Table

| Cluster | Intent | Volume Est. | Page Potential | Priority |
|---|---|---|---|---|
| [Cluster 1] | Commercial | [X/month] | [N pages] | High / Medium / Low |
```

---

## Template 2 — Project Comparison Matrix

```markdown
# Project Comparison Matrix

**Niche:** [niche]

| Project Idea | Demand | Feasibility | Focus | Monetization | Scalability | Maintenance | Uniqueness | Speed | Total |
|---|---|---|---|---|---|---|---|---|---|
| [Project A] | /5 | /5 | /5 | /5 | /5 | /5 | /5 | /5 | /40 |
| [Project B] | /5 | /5 | /5 | /5 | /5 | /5 | /5 | /5 | /40 |
| [Project C] | /5 | /5 | /5 | /5 | /5 | /5 | /5 | /5 | /40 |

**Score interpretation:** 35–40 = build first | 28–34 = secondary | 20–27 = marginal | <20 = do not build

## Score Rationale

### [Project A]
- Demand: [reason for score]
- Feasibility: [reason for score]
- [continue per factor]

**Risk flags:** [any thin content, duplication, or differentiation risks]
```

---

## Template 3 — Recommended Project Brief

```markdown
# Recommended Project Brief

## Project Summary
- **Project name:** [descriptive working title]
- **Site pattern:** [Comparison Database / Directory / Content Tool / Authority Hub / Location Directory]
- **Target niche:** [niche]
- **Primary keyword cluster:** [cluster name]
- **Opportunity score:** [X/40]
- **Monetization model:** [affiliate / lead gen / ads / SaaS / digital product]

## Why This Project
[2–3 sentences stating the specific opportunity, why this scores above alternatives, and what
the site will do better than existing SERP results.]

## Target User
- **Who:** [describe the primary user]
- **What they search:** [example queries]
- **What they want:** [what the ideal result looks like for them]

## Core Value Proposition
[One sentence: "This site helps [user] do [action] by [mechanism]." No marketing language.]

## Risks and Mitigations
| Risk | Severity | Mitigation |
|---|---|---|
| [Thin content at scale] | High/Medium/Low | [strategy] |
| [Competitor with high DA] | High/Medium/Low | [strategy] |
| [Data accuracy over time] | High/Medium/Low | [strategy] |

## Runner-Up Project
- **Name:** [project name]
- **Score:** [X/40]
- **When to build instead:** [condition under which this would be preferred]
```

---

## Template 4 — Site Map

```markdown
# Site Map

**Project:** [project name]
**Pattern:** [site pattern]

## URL Structure

```
/                                   → Homepage
/[primary-category]/                → Category index
/[primary-category]/[entity-slug]/  → Entity profile
/compare/[a]-vs-[b]/               → Comparison page (if applicable)
/[filter-attribute]/[value]/        → Filtered list (if applicable)
/about/                             → About page
/sitemap.xml                        → Auto-generated sitemap
```

## Page Hierarchy

```
Level 0: Homepage (1 page)
Level 1: Category indexes (N pages)
Level 2: Entity profiles / filtered lists (N pages)
Level 3: Comparison pages / sub-pages (N pages)
```

## Page Count Estimates

| Page Type | Count | Generation Method |
|---|---|---|
| Homepage | 1 | Manual |
| Category indexes | [N] | Template |
| Entity profiles | [N] | Programmatic |
| Comparison pages | [N] | Programmatic |
| Filtered lists | [N] | Programmatic |
| **Total** | **[N]** | |
```

---

## Template 5 — Page Template Specification

```markdown
# Page Template Specification

## Template: [Page Type Name]

**URL pattern:** `/[pattern]/`
**Purpose:** [what this page type does for the user]
**Primary intent served:** [Commercial / Informational / Transactional]

### Required Data Fields

| Field | Type | Source | Notes |
|---|---|---|---|
| [field_name] | string/number/boolean | [data source] | [any constraints] |

### Page Sections (in order)

1. **[Section Name]** — [description of content. Required / Optional.]
2. **[Section Name]** — [description. Required / Optional.]
3. **[Section Name]** — [description. Required / Optional.]

### Title Tag Formula

```
[Primary keyword] | [Modifier] | [Brand]
Max 65 characters.
Example: "Best CRM for Freelancers 2025 | ToolSite"
```

### Meta Description Formula

```
[Action verb] [primary topic]. [Key differentiator]. [Call to action].
Max 155 characters.
Example: "Compare the top CRMs for freelancers. See pricing, features, and ratings. Find your best fit."
```

### Differentiation Rule

Each page in this template must differ from others by:
- [Specific unique field or content element]
- [Second unique element]

### Internal Links Required

- Link to: [list of required internal link types from this page type]
```

---

## Template 6 — Internal Linking Map

```markdown
# Internal Linking Map

**Project:** [project name]

## Linking Rules

| From Page Type | Links To | Link Type | Max Links |
|---|---|---|---|
| Homepage | Category indexes | Navigation | All categories |
| Category index | Entity profiles | Body + navigation | All in category |
| Entity profile | Category index | Breadcrumb | 1 |
| Entity profile | Comparison pages | Body | 3–5 |
| Comparison page | Both entity profiles | Body | 2 (required) |
| Comparison page | Similar comparisons | Body | 3–5 |

## Anchor Text Rules

- Use descriptive anchor text. Avoid "click here" or "read more."
- Match anchor text to the title of the target page.
- Do not over-optimize anchor text with exact-match keywords in every link.

## Hub Pages

These pages serve as internal link hubs and must be linked to from every relevant page:
- [Page 1]
- [Page 2]
```

---

## Template 7 — Schema Markup Plan

```markdown
# Schema Markup Plan

**Project:** [project name]

| Page Type | Schema Type | Required Fields | Notes |
|---|---|---|---|
| [Page type] | [Schema.org type] | [field1, field2, field3] | [any special rules] |

## Implementation Notes

- Render schema as JSON-LD in the `<head>` of each page.
- Use the most specific type available. Do not use generic `Thing` or `WebPage` for typed content.
- All schema fields must match visible page content.
- Do not include schema for content that is not on the page.
- Test all schema using Google's Rich Results Test before launch.

## Example: [Page Type] Schema Block

```json
{
  "@context": "https://schema.org",
  "@type": "[SchemaType]",
  "name": "[entity name]",
  "description": "[entity description]",
  "[field]": "[value]"
}
```
```

---

## Template 8 — Content Brief

```markdown
# Content Brief

**Page title:** [title]
**URL:** [url]
**Page type:** [page type]
**Primary keyword:** [keyword]
**Secondary keywords:** [keyword 1, keyword 2]
**Search intent:** [Commercial / Informational / Transactional]

## User Goal

[One sentence: What does the user want to accomplish or learn when they land on this page?]

## Page Objective

[One sentence: What should this page cause the user to do or understand?]

## Required Sections

1. [Section name]: [description of content, word count guidance, data requirements]
2. [Section name]: [same]
3. [Section name]: [same]

## Unique Value Requirements

This page must include:
- [Specific unique element 1]
- [Specific unique element 2]

## Competitor Gap

[What do the top 3 results for this keyword not cover well? What should this page do better?]

## Word Count Target

Minimum: [N words]

## Internal Links to Include

- Link to [page] using anchor text "[text]"
- Link to [page] using anchor text "[text]"
```

---

## Template 9 — Build Checklist

```markdown
# Build Checklist

**Project:** [project name]
**Stack:** [stack]
**Target launch date:** [date]

## Pre-Build
- [ ] Data source identified and accessible
- [ ] Data schema defined and documented
- [ ] All required fields confirmed available in data source
- [ ] Site pattern confirmed
- [ ] URL structure finalized
- [ ] Domain selected and configured

## Build Phase
- [ ] Static site generator configured
- [ ] Homepage built
- [ ] Category index template built and tested
- [ ] Entity profile template built and tested
- [ ] Comparison page template built (if applicable)
- [ ] Filter page template built (if applicable)
- [ ] Internal linking logic implemented
- [ ] Schema markup implemented on all page types
- [ ] Sitemap.xml generation configured
- [ ] Robots.txt configured
- [ ] Canonical tags on all pages
- [ ] Noindex applied to low-value filter combinations
- [ ] 404 page configured

## Pre-Launch
- [ ] All pages reviewed for thin content (sample 10% of generated pages)
- [ ] Schema tested using Google Rich Results Test
- [ ] All internal links verified (no broken links)
- [ ] Page speed tested (target: Lighthouse > 90 on mobile)
- [ ] Mobile layout verified
- [ ] Analytics configured (GA4 minimum)
- [ ] Search Console property verified

## Post-Launch (Week 1–4)
- [ ] Sitemap submitted to Google Search Console
- [ ] Initial crawl confirmed in Search Console
- [ ] Index coverage report reviewed
- [ ] First ranking data reviewed (expect 6–12 weeks for initial results)
```

---

## Template 10 — KPI Measurement Plan

```markdown
# KPI Measurement Plan

**Project:** [project name]
**North Star Metric:** [e.g., organic sessions per month]

## Tracking Setup

| Tool | Purpose | Setup Required |
|---|---|---|
| Google Search Console | Impressions, clicks, average position | Verify domain |
| GA4 | Sessions, engagement, conversions | Install tracking |
| [Optional: Ahrefs / Semrush] | Keyword rankings, backlink tracking | Connect domain |

## KPI Tree

```
North Star: [Organic sessions / month]
├── Indexed pages
│   ├── Pages submitted to sitemap
│   └── Pages approved for indexing (no noindex)
├── Average click-through rate (CTR)
│   ├── Title tag quality
│   └── Schema rich results
└── Average ranking position
    ├── Topical authority score
    └── Backlink profile
```

## Measurement Cadence

| Metric | Frequency | Owner |
|---|---|---|
| Indexed page count | Weekly | [owner] |
| Organic sessions | Weekly | [owner] |
| Average position | Monthly | [owner] |
| Conversion rate | Monthly | [owner] |
| Page pruning review | Quarterly | [owner] |

## Thresholds and Actions

| Metric | Warning Threshold | Action |
|---|---|---|
| Pages indexed / pages submitted | Below 80% | Review robots.txt, canonical tags, thin content |
| Average CTR | Below 2% | Review title tags and schema markup |
| Average position for core cluster | Above position 20 after 3 months | Review content quality and internal linking |
| Sessions with zero conversions | Over 70% for 3 months | Review monetization placement and page intent match |
```
