Six cases for `claude plugin eval`: align (ask first, skip when small, stop on drift), humanize, Arabic, web balance.
Run them deliberately from the repo root: `claude plugin eval adams --concurrency 2`.
This spends API usage (3 runs per case, with and without the plugin); cap it with `--runs 1` or `--max-cost-usd`.
Bash is gated; add `--allow-tools Bash` so the agent can run `adams check`.
`tool_used` graders are with-only indicators and do not count toward the score.
Cases follow `plugin eval --help`: `<case>/prompt.md` plus `<case>/graders/*.md`.
Cases tagged `regression-guard` pass with and without Adams on purpose: they catch a drop in behavior, not a gain. `stop-gate` checks that flagged text triggers a check before the agent finishes.
