# Workflow

How work is stress-tested, debugged, handed off and improved. Patterns adapted from mattpocock/skills (grilling, diagnosing-bugs, handoff, retro, listed on skills.sh), rewritten to fit the team's rules. Load this when someone says "grill me" or "challenge this", a plan or design needs stress-testing, something is broken, failing or slow, a session is ending or getting long, or a session went badly.

## 1. Grill: stress-test a plan before building

Use for big decisions, new products or features, and any plan he asks you to challenge. Think of the plan as a **design tree**: every decision branches into decisions that hang off it.

1. Work in **rounds**. The **frontier** is every open decision whose prerequisites are settled. Ask the whole frontier in one round, at most 4 questions, numbered, each with your recommended answer. Word each question so "yes" accepts the recommendation. When only one question is open, ask only that one.
2. Wait for the answers, then recompute the frontier: settled decisions unblock the ones that depended on them. A question that depends on another open question waits for a later round.
3. Finding facts is your job, never the owner's. If a question needs a fact from the environment (files, tools, logs, the live site), look it up or dispatch a subagent. Ask him only for decisions, access and money.
4. Done when the frontier is empty and nothing is silently assumed. Do not start building until he confirms you share the understanding.

Every recommendation follows `product-principles`: one option, the reason, and a push back on a flaw in the idea.

## 2. Diagnose: anything broken, failing or slow

Two blind attempts without a feedback loop means stop and build the loop. Never guess a third time.

1. **Redact first.** Strip secrets, tokens and personal data from anything you paste, save or hand on.
2. **Build a tight feedback loop** that shows the failure in seconds. Prefer, in this order: a failing test at the seam that reaches the bug; a curl or HTTP script against the dev server; a CLI run with a fixture and a diff of the output; a headless browser script (Playwright, as `web_balance.js` does) asserting on DOM, console or network; a replay of a captured request or event log; a throwaway harness around one function; a fuzz loop for "sometimes wrong"; a bisection harness (`git bisect run`) when it broke between two known states; a differential run of old against new. A human clicking is the last resort, and then guide the person with a script so the loop stays structured. For non-deterministic bugs, raise the failure rate until the loop is reliable. If you genuinely cannot build a loop, say so and ask for the one thing you need.
3. **Reproduce and minimise** until the smallest input or setup still fails.
4. **Hypothesise.** Write 3 to 5 ranked, falsifiable hypotheses and the prediction each makes before you test any.
5. **Instrument one hypothesis at a time.** A debugger or REPL breakpoint beats ten logs; targeted logs at the boundaries that separate hypotheses; never "log everything and grep".
6. **Fix with a regression test.** Turn the minimal repro into a failing test, watch it fail (if you forced the red by mutating code, diff against a pristine copy to prove the mutation landed), apply the fix, watch it pass, re-run the original scenario.
7. **Clean up.** Remove instrumentation and throwaway harnesses, and say what the root cause was.

## 3. Verify before you say done

Code: run the project's build and tests and quote the result. Deliverables: run `scripts/check.py` and quote `ADAMS CHECK: CLEAN`. A step that failed, was skipped or could not be verified is reported as such.

## 3b. Complete output

A partial output is a broken output (merged from the retired full-output-enforcement skill). When he asks for a full file, deliver the full file; for five components, deliver five.

- Banned in code: `// ...`, `// rest of code`, `// implement here`, a bare `TODO` standing in for work, `// similar to above`, `...` replacing omitted code. Banned in prose: "for brevity", "the rest follows the same pattern", "I'll leave that as an exercise", an offer to continue instead of continuing.
- Before answering, count the deliverables the request asks for and compare with what you wrote. Anything missing gets added first.
- Near the output limit, never compress the rest or jump to a conclusion. Finish at a clean breakpoint (end of a function, file or section) and end with `PAUSED, X of Y complete, send "continue" to resume from: <next section>`. On "continue", pick up exactly there with no recap.
- If a simpler version is all that was asked for, say so in one line (a `ponytail:` note); never ship a stub silently.

## 4. Handoff: end of session or before a long task

Auto-compact is set at 50% (see `SKILL.md`), and compaction loses detail, so write the handoff before a long task, not after.

- Save it to the scratchpad or `$TMPDIR`, never the workspace.
- Contents: the goal; state (done, in progress, blocked); decisions made and why; the next 3 steps in order; paths and URLs of the artifacts that matter; which Adams modules or skills the next agent should load; open risks.
- Reference specs, plans, commits and diffs by path or URL instead of copying them.
- Redact secrets and personal data.

## 5. Retro: improve the environment after a bad session

Run when a session was slow, wrong or repetitive. You are improving the environment for future runs, not blaming the session. Read the primary source (the session log or this conversation), then look for:

- **Navigation:** time spent finding a file or fact; add a pointer to the router or a guide.
- **Automated checks:** an error a lint, test or `check.py` rule could have caught; add the rule.
- **Steering size:** instructions in `CLAUDE.md`, `ALWAYS.md` or a guide that are huge, duplicated or change nothing; move them to a guide or delete them.
- **Tool economy:** expensive calls that a script or a smaller query would replace.
- **Information access:** a fact the agent needed and could not see (logs, a live URL, a read-only account); give it access.

Present candidates to the owner by severity. Accepted fixes go into the Adams repo in the same task, then `scripts/selftest.py` (the standing rule: a correction becomes a rule, fixed everywhere).
