# Evals

Seven cases for `claude plugin eval`. They cover asking first, staying quiet on a small task, stopping when a plan breaks, the stop gate, humanize, Arabic and the web check.

Run them from the repo root, and only when the router, the description or the reminder changes:

    claude plugin eval . --runs 2 --concurrency 4 --allow-tools Bash --trust-plugin

A run spends usage on your own Claude account (about 2 to 5 dollars for a full pass). Cap it with `--max-cost-usd`. Bash is gated, so `--allow-tools Bash` lets the agent run `adams check`.

Cases follow `plugin eval --help`: `<case>/prompt.md` plus `<case>/graders/*.md`. Graders marked `arm: with-only` are indicators and do not count toward the score. Cases tagged `regression-guard` pass with and without Adams on purpose, so they catch a drop in behavior and not a gain.
