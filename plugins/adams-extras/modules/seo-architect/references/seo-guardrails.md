# SEO Guardrails

## Purpose

This file defines what is not acceptable in a programmatic static site designed for
search traffic. All outputs from this skill must pass these checks before being
finalized.

These guardrails reflect current search engine quality standards. They are not
optional.

---

## Guardrail 1 — No Doorway Pages

**Definition:** A doorway page is a page created solely to rank for a specific
keyword and redirect or funnel users to a different destination, without providing
value at the page itself.

**Test:** Does the page provide value if a user lands on it directly from search?

- If yes: page is acceptable.
- If no: redesign the page to deliver standalone value, or remove it from the plan.

**Common doorway patterns to avoid:**

- Pages that say "We serve [City]. Click here for our main site."
- Category pages with no content other than a list of links.
- Pages that duplicate the homepage with a different city name in the title.

---

## Guardrail 2 — No Thin Content

**Definition:** Thin content is content with little or no unique value. It may be
short, auto-generated without meaningful differentiation, or copied from another
source.

**Minimum standards per page type:**

| Page Type | Minimum Unique Content |
|---|---|
| Tool or entity profile | At least 5 unique data fields + 100-word unique description |
| Comparison page | At least 3 data points per compared entity + unique recommendation section |
| Filtered list page | At least 5 entities + a unique summary paragraph for that filter |
| Pillar content page | At least 1,500 words of original content |
| Supporting content page | At least 600 words of original content |
| Location page | At least 3 local entities with individual profiles |
| Template or tool page | A functional, complete, usable output (not a stub) |

---

## Guardrail 3 — No Mass Duplication

**Definition:** Duplication occurs when programmatically generated pages have
substantially identical content, differing only in a swapped keyword or location name.

**Test:** Take any two generated pages in the same template. Remove the variable
content (names, numbers, attributes). Is the remaining text identical?

- If yes: add mandatory unique content fields to the template.
- If no: the template passes.

**Approved differentiation strategies:**

1. Unique descriptions written per entity (manual or AI-assisted, reviewed).
2. Unique data combinations (each page shows a unique subset of structured data).
3. Unique editorial sections (e.g., "best for [segment]" that varies by entity attributes).
4. Unique user-generated or third-party data per entity (reviews, ratings, usage stats).

---

## Guardrail 4 — Canonical and Duplication Control

All sites must implement:

1. Canonical tags on all pages pointing to the preferred URL version.
2. Noindex on facet/filter combinations that produce near-duplicate results.
3. A defined rule for which filter combinations are indexable vs. crawlable-only.
4. Pagination handled with `rel="next"` / `rel="prev"` or load-more patterns.
5. A clear policy on parameter handling (e.g., `?sort=` parameters should be
   noindexed or excluded from sitemap).

**Indexable filter rules:**

Index a filter combination only if:
- It has a minimum of 5 entities (for directories).
- It has a distinct keyword pattern with search demand.
- The resulting page has a unique title, description, and introductory paragraph.

---

## Guardrail 5 — Information Architecture Integrity

The site structure must:

1. Have a clear hierarchy: homepage → categories → sub-categories → individual pages.
2. Ensure every page is reachable within 3 clicks from the homepage.
3. Avoid orphan pages (pages with no internal links pointing to them).
4. Avoid crawl traps (infinite or near-infinite pagination without `noindex`).
5. Use consistent URL patterns across page types.

---

## Guardrail 6 — Schema Markup Accuracy

Schema markup must:

1. Match the actual content on the page. Do not add schema fields that are not
   present or visible on the page.
2. Use the most specific applicable schema type.
3. Not be used manipulatively (e.g., fake review counts, inflated ratings).

**Recommended schema types by page pattern:**

| Page Type | Schema Type |
|---|---|
| Tool/product profile | SoftwareApplication, Product |
| Comparison page | ItemList, Table |
| Directory entity | LocalBusiness, Organization |
| Pillar content | Article, HowTo, FAQPage |
| Template/tool page | HowTo, FAQPage |
| Location page | LocalBusiness (multiple), Place |

---

## Guardrail 7 — Sustainable Differentiation

Before finalizing the build plan, answer these questions:

1. **Data advantage:** Does this site have access to data that competitors do not?
   If no, what will make the content unique?
2. **Editorial layer:** Is there a human or AI-reviewed editorial layer that prevents
   mass publishing of unreviewed content?
3. **Update cadence:** Is there a realistic plan to keep data accurate after launch?
4. **Page pruning policy:** Is there a rule for removing or consolidating pages that
   fail to get traffic within 6 months?

If any of these answers is unclear, flag it as a risk in the build plan.

---

## Red Flags Checklist

Before submitting any build plan, check all items below. Flag any that are present.

- [ ] Pages with no unique content beyond a swapped variable.
- [ ] Filter combinations that produce fewer than 5 results.
- [ ] Category pages with no content other than links.
- [ ] Pages where the primary purpose is to capture a keyword, not serve the user.
- [ ] Schema markup that does not reflect real page content.
- [ ] No plan for updating or pruning pages over time.
- [ ] URL structures that create infinite or near-infinite crawl depth.
- [ ] Duplicate titles or meta descriptions across multiple pages.
- [ ] Internal linking that is circular without a clear hierarchy.
- [ ] Monetization that requires deceptive placement or hidden intent.
