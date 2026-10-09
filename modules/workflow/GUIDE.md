# Workflow

How work is stress-tested, debugged, handed off and improved. Methods for diagnosing bugs, handoff and retro, written to fit the team's rules. Load this at the start of any non-trivial task (it fires automatically), when someone says "challenge this" or "poke holes", a plan or design needs stress-testing, something is broken, failing or slow, a session is ending or getting long, or a session went badly.

## 1. Align: ask first, automatically

Runs on its own. Nobody has to say "ask me". The goal is that the work lands on what the user actually needs, and that nothing drifts while it is built. Think of the plan as a **design tree**: every decision branches into decisions that hang off it. "Challenge this" or "poke holes" means the same loop, run harder.

**When it fires (any one is enough):**
- A new feature, product, page, flow, deck, campaign or refactor, or any task with more than one reasonable reading.
- A decision that is costly or slow to reverse: schema, pricing, public copy, deletes, deploys, money, other people's accounts.
- Missing input you cannot find: audience, goal, success measure, constraints, tone, deadline.
- Mid-work drift: the scope grew, a finding contradicts the plan, an assumption turned out false, a second approach looks better, or you are about to touch something the request did not name.

**Skip it** for a clear, small, reversible task (a typo, a rename, a one-line fix, a factual question). Then act, and state the one assumption you made.

**The loop:**
1. **Read the docs first.** Before asking anything, read what already answers it: the project's `CLAUDE.md`, `DESIGN.md`, README, plans, specs, decision notes, recent commits, the code and the live site. Finding facts is your job, never the user's; dispatch a subagent if it is a big search. Ask only for decisions, taste, access and money.
2. **Work in rounds.** The **frontier** is every open decision whose prerequisites are settled. Ask the whole frontier in one round, at most 4 questions, numbered. A question that depends on another open one waits for the next round. When only one is open, ask only that one.
3. **Every question carries a recommendation.** Use the `AskUserQuestion` tool when it exists: 2 to 4 options, your recommended option first and marked "(Recommended)", each option with its trade-off in one line. Without the tool, number the questions in the reply and word each one so "yes" accepts the recommendation. The recommendation is the best practice for this exact situation, drawn from the project's docs, the stack in use, the user's stated goal and what you learned in this session, never a generic default. Say why in one line, and push back on a flaw in the idea (`product-principles`).
4. **Offer what they did not think of.** If a better approach, a missing requirement, a risk or a cheaper path exists, say it as a question with a recommendation, not as a lecture.
5. **Record the answers.** Settled decisions are appended as short dated lines to `.adams/decisions.md` in the project root (create it if missing; for a multi-step task only). The SessionStart hook reloads that file after a restart or compaction. Never invent new doc files for a small task.
6. **Done when the frontier is empty and nothing is silently assumed.** Restate the shared understanding in 3 lines or fewer, then build.

**While building, check drift at checkpoints** (after the plan, before the first irreversible step, when something unexpected appears, before reporting): compare the work with the settled decisions. If it deviates, stop, say what changed and why, and ask with a recommendation before continuing. Never widen scope on your own. A drift question is short: what changed, your recommended action, the cost of each choice.

**Never ask** what the code or docs already answer, what a sensible default covers (state the default instead), or "should I proceed?". More than 4 questions in a round means you have not read enough yet.

## 3. Verify before you say done

Code: run the project's build and tests and quote the result. Deliverables: run `scripts/check.py` and quote `ADAMS CHECK: CLEAN`. A step that failed, was skipped or could not be verified is reported as such.

## 3b. Complete output

A partial output is a broken output. When he asks for a full file, deliver the full file; for five components, deliver five.

- Banned in code: `// ...`, `// rest of code`, `// implement here`, a bare `TODO` standing in for work, `// similar to above`, `...` replacing omitted code. Banned in prose: "for brevity", "the rest follows the same pattern", "I'll leave that as an exercise", an offer to continue instead of continuing.
- Before answering, count the deliverables the request asks for and compare with what you wrote. Anything missing gets added first.
- Near the output limit, never compress the rest or jump to a conclusion. Finish at a clean breakpoint (end of a function, file or section) and end with `PAUSED, X of Y complete, send "continue" to resume from: <next section>`. On "continue", pick up exactly there with no recap.
- If a simpler version is all that was asked for, say so in one line (a `shortcut:` note); never ship a stub silently.

## 5. Execution loop (parallel agents)

Each task runs in its own git worktree cut from `origin/<base>`; never switch branches in the main checkout and never stack on an unmerged dependency. Mark `review` when the PR opens and `done` when it merges, and reply in two lines per PR. Rules, hand-off block and CI advice: `references/execution-loop.md`.

## On demand

- Diagnose something broken, failing or slow: `references/diagnose.md`.
- Handoff at session end or before a long task: `references/handoff.md`.
- Retro after a bad session: `references/retro.md`.
- Parallel agents, PRs and `/ship`: `references/execution-loop.md`.
- Load only the one the task needs.
