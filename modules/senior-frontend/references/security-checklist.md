# Security checklist (Next.js, Supabase, Stripe, Vercel)

Run it when you build or review auth, payments, an API route, a server action or a form. Distilled from public API security guidance and two retired checklists. Every box is a yes or no you can check in the code or the running app, never a feeling.

## Who may do what
- Every route handler, server action and RPC checks the signed-in user and what that user may touch. The check lives on the server, never only in the UI.
- Object level: the id in the URL or body belongs to the caller (tenant or owner filter in the query, or an RLS policy). Property level: the caller may read and write every field returned or accepted.
- Supabase: RLS is on for every table that holds user data, with a policy per role and operation. The service-role key never reaches the client, a `NEXT_PUBLIC_*` variable or a log.
- Roles are checked on the server for admin routes (the project's own guard), not by hiding links.

## Input and output
- Validate every input at the boundary with a schema (Zod): type, length, format, allowlist. Reject, never silently coerce.
- Queries are parameterised or go through the ORM or Supabase client. No string-built SQL, no `eval`, no `new Function`, no user input in file paths.
- Rendered HTML from users is escaped or sanitised. File uploads check type, size and a server-generated name.
- A URL fetched on behalf of a user is validated against an allowlist (SSRF).
- Error responses say what the caller needs and nothing more: no stack traces, SQL or internal ids.

## Fail closed
- Auth error, parse error or timeout means deny, reject or abort with a limit, never allow or retry forever.
- No catch-all that swallows an error on a security operation.
- Check-then-act on balances, credits or limits is atomic (a transaction or a unique constraint), so two requests cannot both pass.

## Payments and webhooks
- Stripe webhooks verify the signature on the raw body before anything runs, and handlers are idempotent (store the event id).
- Prices, amounts and plan ids come from the server, never from the client.
- Entitlements follow the verified webhook or a server read, not a query string or a client flag.

## Secrets and config
- No secret in the repo, a bundle, a log or a screenshot. `.env*` is git-ignored; a leaked key is rotated, not just deleted.
- `NEXT_PUBLIC_*` holds only values safe to publish. Environment variables are validated at boot.
- Dependencies: lockfile committed, `npm audit` (or the project's scanner) reviewed before a release, no unpinned install scripts.

## Abuse limits
- Rate limits on sign-in, sign-up, password reset, OTP, contact forms and any expensive endpoint, stricter than on normal routes, keyed by user and IP. Bot protection (Cloudflare Turnstile) on public forms.
- Sessions expire, cookies are `HttpOnly`, `Secure` and `SameSite`, and CORS lists exact origins.

## Evidence
Cite the file and line, or the request and response you ran, for each box you tick. A box you could not verify is reported as unverified.
