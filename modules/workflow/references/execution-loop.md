# Execution loop for parallel agents and pull requests

Load when work is split into tasks that agents run in parallel sessions and a person reviews the pull requests. The goal is a short path from "the PR is open" to "merged, tracker updated, next prompt in hand", with a person asked only when it matters.

## 1. One task, one worktree

- Each task runs in its own git worktree cut from `origin/<base>`: `git fetch origin && git worktree add ../<name> -b <branch> origin/<base>`. The branch name carries the task id (`feat/T-014-short-title`).
- Never switch branches in the main checkout. It stays on the base branch so it can be pulled after every merge.
- Remove the worktree once the PR is open (`git worktree remove ../<name>`). The branch stays until the PR is merged; never delete an unmerged branch.

## 2. Dependencies: no stacking

- Every execution prompt names its dependencies (`Depends on: T-012, T-013` or `none`). The tracker holds the same list in the optional field `- depends: T-012, T-013`.
- A dependency that is not merged: stop and say so in one line. Do not branch from another task's branch and do not copy its changes.
- `adams next` lists the todo tasks whose dependencies are done. Those are safe to run at the same time, one per session.

## 3. Status follows the PR

- When the PR opens: `adams track set T-014 review --evidence "PR #123 opened"`.
- When it merges: `adams ship 123 T-014 T-015` marks it done with the PR and merge commit as evidence and copies T-015's prompt. `adams track set` edits the task in place and refuses a change that would add a lint error.
- `verified` is still earned at runtime, later, with its own evidence (`modules/senior-frontend/references/execution.md`).

## 4. Review and merge

- `adams watch` lists your open PRs with task id, size and risk tier. `adams ship PR TASK` waits for the fast checks and merges, or stops with one line saying which check failed.
- `/ship` (the slash command) commits this session's files by name, pushes, opens the PR and merges every open PR of yours. It asks one question for all high-risk PRs, never one per PR.
- Risk tiers come from the changed paths: high (migrations, SQL, auth and permissions, payments and billing, env files, secrets, CI config, deletion and purge code), low (docs, markdown content, generated files, lockfiles, build output), normal for the rest. A high PR is never merged without a yes.
- After each PR, reply in two lines: what shipped, what is left.

## 5. Slow suites and CI

- A slow suite that is not a required check runs on the base branch after the merge (list it in `skip_checks` so `ship` does not wait for it). If it fails, fix it before the next merge.
- Add path filters to CI so a docs-only or content-only PR skips the heavy suites. The fast checks then finish in minutes and the loop stays short.

## 6. The prompt ends with one fixed hand-off block

Every execution prompt ends with the instruction "Finish with the hand-off block, nothing before or after it", and the block is this:

```
Hand-off
Task: T-014 Short title (PR #123)
Depends on: T-012 (merged) | none
Files changed: path, path (+N -M)
Checks: <command>: <result>; <command>: <result>; not run: <what, why>
Choices made: <one line each, with the reason>
Left: <what is not done or what the reviewer must look at> | nothing
```

The reviewer reads this block instead of the whole session. A missing line is a defect in the prompt, not in the reviewer.

## Settings

`.adams/ship.json` is optional and owned by the project: base branch, auto-merge answer, checks not to wait for, tracker and prompt file paths, risk patterns, wait cap. The format is in `docs/OPERATIONS.md`.
