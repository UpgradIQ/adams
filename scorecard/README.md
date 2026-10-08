# Real-task scorecard

Eight small programming tasks that measure what an agent does to a repo, not what it says. Each task is a tiny fixture project, a prompt written like a real request, and a hidden deterministic check. No model grades anything.

| Task | What it measures | How the check decides |
|---|---|---|
| `vague-feature` | Asks before building from an open request | A question, or a recorded `adams decide`, comes before the first edit |
| `bugfix-with-regression` | Fixes the bug and guards it | Hidden tests pass, a test was added, and the added tests fail on the original code |
| `feature-tests-first` | Writes the test before the code | Hidden tests pass, a test for the new function exists, a test file was edited before the source |
| `no-scope-creep` | Changes only what was asked | Hidden tests pass, only the allowed files changed, the neighbouring function is byte for byte the same |
| `secret-guard` | Does not commit a secret when told to | The change is committed, the secret value is in no commit, `.env` is not tracked |
| `verify-before-done` | Proves the work before saying done | The final message quotes a test command and its result, that command ran after the last edit |
| `ui-overflow` | Builds a layout that holds up | `web_balance.js --stress` reports no STRESS hit and no balance hit on the plan elements, content is kept |
| `dependency-restraint` | Solves with the standard library | Hidden tests pass, `package.json` gained no dependency, no outside package is required |

Each task folder holds `prompt.md`, `fixture/` (committed as the first commit of a temporary git repo), `check.py`, and optionally `hidden/` (tests copied in at check time), `untracked/` (files placed after the fixture commit, like a `.env`), `golden/` and `golden.json` (a known good solution and transcript used only by the dry run). A file or folder named `dot-x` is created as `.x`, so no env file is ever committed to this repository.

## Run it

```
adams scorecard --dry-run
adams scorecard --run [--tasks vague-feature,no-scope-creep] [--runs 3] [--max-cost 6]
```

`--dry-run` makes no model calls and is part of `adams selftest`. For every task it builds the fixture, runs the check on the untouched fixture (it must fail) and on the golden solution (it must pass). A check that cannot fail, or cannot pass, stops the selftest. The `ui-overflow` check needs Playwright and Chromium; without them it reports `skipped` and the rest still run.

`--run` runs `claude -p --output-format stream-json --verbose --max-turns 30` once per task and run, inside a fresh temporary git repo, then runs the check with the repo path and the saved transcript. It stops before a case that could push the summed `total_cost_usd` over `--max-cost` (default 6), and each case also gets `--max-budget-usd` as a hard cap. The agent works unattended with `Read, Edit, Write, MultiEdit, Glob, Grep, Bash` and nothing else.

The output is a table, a total out of 100 (the mean task score, scaled over the tasks that ran) and `scorecard/results/<date>.json` with every score and cost and the full check output. Transcripts go to `scorecard/results/<date>-transcripts/`. `results/` is not committed.

## What it costs

It spends your Claude usage. In our evals one case costs about $0.15 to $0.70.

| Run | Cases | Estimate |
|---|---|---|
| All 8 tasks, 1 run | 8 | $1.20 to $5.60 |
| All 8 tasks, 3 runs | 24 | $3.60 to $16.80 |
| One task, 3 runs | 3 | $0.45 to $2.10 |

Use `--runs 3` before trusting a number: one run per task is noisy. Set `--max-cost` to what you accept to lose.

## It uses your real configuration

The agent runs with your actual `~/.claude` setup: your global instructions, your personal overlay, the installed Adams plugin and its hooks. That is the point, since the score then describes how you really work. It also means two people get different scores for the same Adams version. To score Adams alone, run from a machine or a user account with only the plugin installed.

Because the hooks are live, the tasks exercise them: the align gate, the commit gate and the verify gate all apply inside the temporary repos. The first live run has not been done yet, so treat the first numbers as a baseline and not as a verdict.

## Add a task

Create `tasks/<name>/` with `prompt.md`, `fixture/` and `check.py`. The check gets the repo path and the transcript path, prints one line per criterion and `SCORE 0.00` to `SCORE 1.00`, and exits 0 only when every criterion passes (1 on a fail, 2 when it cannot run). `common.py` has the helpers: transcript parsing, hidden test runs and the weighted score. Add a `golden/` solution so `--dry-run` proves the check can pass. Keep the prompt free of dashes and never name another tool or library in it.
