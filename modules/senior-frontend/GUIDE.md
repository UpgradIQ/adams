# Senior Frontend

Spec-first frontend engineering for a Next.js, Vercel, Supabase, Stripe, Sentry stack. Acts as Chief Architect and Senior Engineer for component design, data flow, performance, and production hardening.

## When To Use

Use this skill for any of the following:

- Build or refactor a React or Next.js component, page, layout, or route handler.
- Design client/server data flow across Server Components, Client Components, and Server Actions.
- Audit bundle size, hydration cost, rendering strategy, or Core Web Vitals.
- Implement auth flows with Supabase, payment flows with Stripe, or error tracking with Sentry.
- Review or harden a frontend pull request.
- Translate a Spec-Kit specification into implementation-ready code.

## Operating Rules

1. **Spec-first**: if a Spec-Kit spec exists, read it before coding. If none exists for a new feature, prompt the user to generate one via `specify generate feature <name>`.
2. **Decision-ready outputs**: state trade-offs, constraints, and one recommendation per decision.
3. **Minimal vendor lock-in**: prefer framework-native primitives; isolate SDK calls behind thin adapters.
4. **Type safety**: TypeScript strict mode; no `any`; Zod for runtime boundaries.
5. **Accessibility**: WCAG 2.2 AA minimum; semantic HTML before ARIA.
6. **Performance budget**: state the budget before optimizing; measure with Lighthouse and `next build` output.

## Core Workflows

### 1. Component Design

Sequence:

1. Confirm the component's role: Server Component, Client Component, or hybrid.
2. Define props with TypeScript and Zod schemas where inputs cross trust boundaries.
3. Compose from shadcn/ui primitives; extend with Tailwind utility classes.
4. Extract reusable logic into hooks under `src/hooks/`.
5. Add unit tests (Vitest or Jest) and a Storybook entry when the component is shared.

Output contract:

- File path under `src/components/`.
- Named exports only; no default exports for shared components.
- Co-located styles via Tailwind; no CSS modules unless required.
- JSDoc on public props.

### 2. Page and Route Design

Sequence:

1. Choose rendering mode: static, dynamic, streaming, or ISR. Justify with data freshness and latency needs.
2. Place data fetching in Server Components or Route Handlers; never in Client Components unless necessary.
3. Use Server Actions for mutations; return typed results; handle errors with `try/catch` and Sentry capture.
4. Add `loading.tsx`, `error.tsx`, and `not-found.tsx` where user-visible states exist.
5. Gate authenticated routes via Supabase session checks in `middleware.ts` or layout guards.

### 3. Performance Audit

Sequence:

1. Run `next build`; capture route sizes and First Load JS.
2. Identify routes exceeding budget (default: 200 KB First Load JS for marketing, 300 KB for authenticated app).
3. Classify waste: oversized client bundles, unneeded `"use client"`, large dependencies, unoptimized images, blocking third-party scripts.
4. Apply fixes in priority order: move to Server Components, dynamic import heavy client code, replace heavy libraries, use `next/image` and `next/font`, defer third-party scripts.
5. Re-measure; report delta.

### 4. State Management

Selection rule:

| State scope | Tool |
|---|---|
| URL or route state | Next.js router, searchParams |
| Server data | React Query or SWR; Server Components where possible |
| Cross-component client state | Zustand or React Context |
| Form state | React Hook Form with Zod resolver |
| Session and auth | Supabase client |

Avoid Redux unless the app already uses it.

### 5. Auth, Payments, Observability

- **Supabase**: use `@supabase/ssr` for Next.js App Router; session in middleware; RLS on every table; never expose service-role keys to the client.
- **Stripe**: server-side intent creation; client confirms with `@stripe/stripe-js`; webhooks handled in Route Handlers with signature verification.
- **Sentry**: initialize in `sentry.client.config.ts` and `sentry.server.config.ts`; capture handled errors explicitly; scrub PII.

## Code Standards

- **Naming**: PascalCase for components, camelCase for hooks (`useX`), kebab-case for files.
- **Imports**: absolute paths from `@/`; group external, internal, styles.
- **Error boundaries**: one per major route segment.
- **Environment variables**: `NEXT_PUBLIC_*` only when required on the client; validate with Zod at boot.
- **Testing**: unit for utilities and hooks; integration for forms and flows; Playwright for critical paths.
- **Security**: for auth, payments, API routes, server actions and forms, walk `references/security-checklist.md` and report each box with evidence.

## Spec-Kit Integration

When the user requests a new component, API surface, or feature:

1. Run `specify check` to confirm the workspace is valid.
2. Generate the relevant spec:
   - Feature: `specify generate feature <name>`
   - Component: `specify generate component <name>`
   - API: `specify generate api <name>`
3. Implement against the spec; update the spec when behavior changes.
4. Keep specs and code in sync; treat drift as a bug.

## Output Formats

### Component delivery

ALWAYS return in this order:

1. File tree of new or changed files.
2. Full file contents, one fenced block per file.
3. Commands to run (install, lint, test).
4. Verification checklist (build passes, tests pass, bundle delta).

### Audit delivery

ALWAYS return in this order:

1. Scope and budget.
2. Findings table: route, current size, target, waste category.
3. Prioritized actions with expected impact.
4. Code patches or diffs.
5. Re-measurement plan.

## Anti-Patterns

Avoid these:

- `"use client"` at the top of a page without need.
- Fetching in `useEffect` when a Server Component would work.
- Storing server data in Zustand or Context.
- Importing full icon libraries; import per-icon instead.
- Using `<img>` over `next/image`.
- Blocking the main thread with synchronous third-party scripts.
- Exposing Supabase service-role keys or Stripe secret keys to the client.

## Assumptions

- Package manager: `pnpm` unless the repo uses another.
- Node: LTS.
- Next.js: App Router, latest stable.
- Styling: Tailwind CSS plus shadcn/ui.
- Hosting: Vercel.

Override any assumption by stating the constraint in the prompt.

## SaaS revamp program

**When to use:** the task is to revamp or audit a SaaS (UI, UX, CX, conversion, onboarding, pricing, dashboards, admin, docs) or to plan and track that work from an early version to enterprise production. Load `modules/product-principles/GUIDE.md` first (truth, focus law, ethical persuasion). Project rules (design tokens, width, deploy and push rules) come from the project's own `DESIGN.md` and `AGENTS.md`. Canonical layout values are in `modules/line-balance/GUIDE.md`.

```
Audit --> Track --> Plan --> Execute --> Verify
  |         |         |         |          |
  v         v         v         v          v
scorecard  track.md  funnel +  one task    gates, closure,
(runtime)  (1 file)  ICE       at a time   verdict
```

| Phase | What happens | Load |
|---|---|---|
| 1 Audit | Walk the running product, score 12 lenses and Nielsen 10 with runtime evidence, verdict per capability (Preserve, Redesign, Rebuild, Remove) | `references/audit-scorecard.md` |
| 2 Track | Create the single tracker `.planning/track.md` from the audit; lint it | `references/execution.md`, `references/track-template.md`, `scripts/track.py lint` |
| 3 Plan | Order tasks dependency-first; for conversion work write the experiment record; define each page's job and standard | `references/page-standards.md`, `modules/product-principles/references/funnel-map.md`, `conversion-psychology.md`, `dark-patterns.md` |
| 4 Execute | One task at a time from "Next immediate task"; build to the page standards; write the closure report | `references/execution.md`, `references/page-standards.md` |
| 5 Verify | Run the quality gates, balance check, live check; stop only at 0 Critical and 0 High; give the final verdict | `references/execution.md` (gates, stop rule), `scripts/check.py` |

Render the tracker for the owner with `adams track render .planning/track.md OUT.html`.

### Dashboard template (one for every dashboard page)

Product screens share ONE template; only marketing pages vary.

1. Title, one-line purpose, and a "How to" link to the docs article.
2. Status line: state and last updated.
3. At most 4 tabs.
4. Main area: what to do now, at most 3 items. Details on demand.

Options rule: personal options live in Settings; workspace options in Settings > Workspace; a product's own options only in that product's Settings tab. Detail in `references/page-standards.md`.

### The 5 states (every screen defines all five)

| State | Must show |
|---|---|
| Empty | An invitation to act, with the one next step |
| Loading | Skeleton in the final layout, no layout shift |
| Error | What happened and how to fix it, no apology |
| Success | Small celebration and the next step |
| Connected | Proof: last read time, 3 real values read, what it unlocked, Test now and Reconnect; saved settings shown as values with Edit, never an empty field beside "Connected" |
