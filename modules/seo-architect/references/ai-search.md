# AI search (GEO/AEO) reference

Facts the audit script relies on, and what is still unproven. Vendor crawler names and policies change: confirm them in each vendor's current documentation before acting on a result.

## Crawlers and robots.txt

| User agent | Operator | Used for |
|---|---|---|
| `GPTBot` | OpenAI | Collecting content that may train models |
| `OAI-SearchBot` | OpenAI | Indexing pages for ChatGPT search results |
| `ChatGPT-User` | OpenAI | Fetching a page when a user asks for it |
| `ClaudeBot` | Anthropic | Collecting content that may train models |
| `PerplexityBot` | Perplexity | Indexing pages for Perplexity answers |
| `Google-Extended` | Google | A robots.txt token only: controls use of content for Gemini, no separate crawler |

- Blocking training bots (`GPTBot`, `ClaudeBot`) and allowing search bots (`OAI-SearchBot`, `PerplexityBot`) is a valid, common choice. The audit reports every blocked bot so the owner confirms it is intended.
- Google AI Overviews use the normal Googlebot index and its snippet controls (`nosnippet`, `max-snippet`). `Google-Extended` does not control them.
- robots.txt is a request, not access control. Content that must stay private needs authentication.

## llms.txt

- A proposal (2024) for a Markdown file at `/llms.txt` that lists the main pages of a site for language models.
- Unverified: no major AI search provider has confirmed that it reads the file or that it changes retrieval or citations. Treat it as low cost and unproven. The audit warns when it is missing but does not fail.

## Structured data

- JSON-LD that does not parse is ignored by every consumer. The audit fails on it.
- Recommended types: `Organization` (with `name`, `url`, `logo`, `sameAs`) on the home page, `Article` or `BlogPosting` on posts, `Product` and `Offer` on product and pricing pages, `FAQPage` only when the questions and answers are visible on the page.
- Google restricts FAQ rich results to well-known government and health sites (since 2023). `FAQPage` markup can still describe the content to other parsers.
- Unverified: that any structured data raises the chance of being cited in an AI answer. It is a sound way to state facts unambiguously, not a ranking lever.

## Page content that is easy to cite

- Put the direct answer in the first sentences under a heading. Phrase headings the way people ask.
- State facts with a number, a date and a source. Keep the author and the update date visible.
- One h1, one topic per page, a canonical URL, a 10-70 character title and a 50-170 character description. These are conventions for display and consistency, not hard limits from a search provider.
- Write the brand name the same way everywhere (JSON-LD, title, `og:site_name`, body). Inconsistent spelling splits one entity into several.
- Content that needs JavaScript to render may not be seen by crawlers that do not run it. Serve the main text in the HTML.

## Measuring

- Server logs: count requests from the user agents above, by path.
- Referrals: sessions from `chatgpt.com`, `perplexity.ai`, `gemini.google.com` and similar hosts.
- Manual prompts: ask the questions your buyers ask in each assistant, note whether and how the site is cited, repeat monthly. Answers vary between runs, so record the date and the exact prompt.
- No tool gives a reliable share of voice across assistants. Report what was observed, not an index.

## What the audit does not check

Page speed, rendering of JavaScript, backlinks, entity presence outside the site (Wikipedia, Wikidata, reviews) and whether a bot fetched a page. Say so when reporting a clean result.
