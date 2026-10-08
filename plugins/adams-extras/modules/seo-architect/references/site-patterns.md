# Static Site Patterns for SEO

## Overview

This file defines the standard static site patterns suitable for programmatic SEO.
Each pattern has a description, best-fit keyword intent, example niches,
architecture rules, and typical page count.

---

## Pattern 1 — Comparison Database

**What it is:** A structured database of tools, products, or services with
filterable comparison pages and individual profile pages.

**Best fit:** Commercial intent. "Best X for Y", "X vs Y", "X alternatives".

**Example niches:** SaaS comparisons, financial products, HR tools, hosting providers.

**Architecture:**

```
/                           → Homepage (category overview)
/[category]/                → Category index (e.g., /project-management/)
/[category]/[tool]/         → Individual tool profile
/compare/[tool-a]-vs-[tool-b]/  → Comparison page
/[category]/best-for-[use-case]/  → Use-case filtered list
```

**Data schema (per tool):**

| Field | Type | Notes |
|---|---|---|
| name | string | Tool name |
| slug | string | URL-safe identifier |
| category | string | Primary category |
| tagline | string | One-line description |
| pricing_from | number | Starting price (USD/month) |
| free_plan | boolean | Whether a free tier exists |
| use_cases | array | List of supported use cases |
| integrations | array | Key integrations |
| rating | number | Internal or aggregated score |
| last_updated | date | Data freshness indicator |

**Internal linking logic:**

- Each tool page links to: its category index, top 3 comparison pages, top 3 alternatives
- Each comparison page links to: both tool profiles, "similar comparisons" section
- Each category index links to: all tool profiles in that category, top comparison pages

**Typical page count:** 100–2,000+ pages depending on tool count and comparison pairs.

**Differentiation requirement:** Each profile must include at least 3 unique data points
not available on the tool's own website (e.g., independent use-case ratings, user
segment fit, integration depth scores).

---

## Pattern 2 — Directory with Faceted Filtering

**What it is:** A directory of entities (businesses, resources, people, locations)
with filterable pages for each attribute combination.

**Best fit:** Informational and transactional intent. Local, niche, or attribute-based
searches.

**Example niches:** Startup accelerators, freelance platforms, grant databases,
industry events.

**Architecture:**

```
/                           → Homepage
/[type]/                    → Top-level category
/[type]/[attribute]/        → Attribute-filtered list (e.g., /accelerators/europe/)
/[type]/[attr-a]/[attr-b]/  → Multi-attribute filter (e.g., /accelerators/europe/fintech/)
/[type]/[slug]/             → Individual entity profile
```

**Data schema (generic):**

| Field | Type | Notes |
|---|---|---|
| name | string | Entity name |
| slug | string | URL identifier |
| type | string | Primary category |
| attributes | object | Key-value filter attributes |
| description | string | 100–300 word unique description |
| external_url | string | Official site link |
| verified | boolean | Data quality flag |

**Internal linking logic:**

- Entity profile links to: parent category, related entities in same attributes
- Filtered pages link to: broader category, more specific sub-filters
- Homepage links to: all top-level categories, featured entities

**Typical page count:** 50–5,000+ pages.

**Differentiation requirement:** Each filtered page must serve a specific search intent
not served by the parent category. Avoid creating filter combinations with fewer than
5 entities unless the topic has demonstrable search demand.

---

## Pattern 3 — Programmatic Content Tool

**What it is:** A static site where each page answers a specific question or
provides a calculation, reference table, or template for a defined input combination.

**Best fit:** Informational and transactional intent. "How to X", "X calculator",
"X template", "X for Y context".

**Example niches:** Financial calculators, legal clause libraries, marketing templates,
code snippet databases.

**Architecture:**

```
/                           → Homepage (tool overview)
/[tool-type]/               → Tool category
/[tool-type]/[variant]/     → Specific tool or output page
/templates/[use-case]/      → Template pages
/examples/[context]/        → Example pages
```

**Data schema (per page):**

| Field | Type | Notes |
|---|---|---|
| title | string | Page title |
| slug | string | URL identifier |
| tool_type | string | Category |
| input_context | string | What the tool is for |
| output_content | string/object | The tool output (rendered at build time) |
| related_tools | array | Links to related pages |

**Internal linking logic:**

- Each tool page links to: parent category, 3–5 related tools, one "how to use" guide
- Category pages link to: all tools in category, cross-category bridges

**Typical page count:** 20–500+ pages.

**Differentiation requirement:** Each page must produce an output that is genuinely
useful standalone. Pages that only restate a formula without context do not qualify.

---

## Pattern 4 — Topical Authority Hub

**What it is:** A structured content site organized by topic clusters with pillar
pages and supporting sub-pages designed to establish topical authority.

**Best fit:** Informational intent. "How to", "guide to", "what is X", "X explained".

**Example niches:** HR compliance guides, startup financing education, supply chain
management, digital marketing methodologies.

**Architecture:**

```
/                               → Homepage
/[pillar-topic]/                → Pillar page (2,000+ words)
/[pillar-topic]/[sub-topic]/    → Supporting content page
/[pillar-topic]/[glossary]/     → Glossary or definition pages
/[pillar-topic]/[checklist]/    → Checklist or template pages
```

**Internal linking logic:**

- Pillar page links to: all supporting pages in its cluster
- Supporting pages link to: parent pillar, 2–3 sibling supporting pages
- Glossary/checklist pages link to: parent pillar, related checklists/glossary entries

**Typical page count:** 20–200 pages.

**Differentiation requirement:** Pillar pages must cover the topic more completely than
the top 3 SERP results. Supporting pages must address a specific sub-question not
fully answered by the pillar or by competitors.

---

## Pattern 5 — Location-Based Directory

**What it is:** A directory where the primary differentiator is geographic location,
combined with a service or entity type.

**Best fit:** Informational and transactional intent. "[Service] in [Location]".

**Example niches:** Business service directories, event listings, professional
directories, coworking spaces.

**Architecture:**

```
/                                   → Homepage
/[country]/                         → Country index
/[country]/[city]/                  → City index
/[country]/[city]/[service-type]/   → Service category in city
/[country]/[city]/[service-type]/[entity-slug]/  → Individual profile
```

**Internal linking logic:**

- City pages link to: all service categories in that city, neighboring cities
- Profile pages link to: city index, same service type in city, related services
- Country pages link to: all cities with data

**Typical page count:** 100–10,000+ pages depending on geographic and entity coverage.

**Differentiation requirement:** Each location page must contain entity data unique to
that location. Do not create location pages with fewer than 3 entities or no data.

---

## Pattern Selection Matrix

| Pattern | Best When | Avoid When |
|---|---|---|
| Comparison Database | Clear set of comparable entities. Commercial intent. | Entities change too frequently. Data is hard to standardize. |
| Directory with Facets | Many attributes per entity. Filter-based search behavior. | Too few entities per filter combination. Low search demand for filtered views. |
| Programmatic Content Tool | Repeatable question-answer or template structure. | Output requires real-time data. Static rendering is insufficient. |
| Topical Authority Hub | Informational niche with clear sub-topic structure. | Topic is already fully dominated by high-authority publishers. |
| Location Directory | Strong local search demand. Many entities per location. | No reliable source of location-specific data. |
