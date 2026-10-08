## 2. Diagnose: anything broken, failing or slow

Two blind attempts without a feedback loop means stop and build the loop. Never guess a third time.

1. **Redact first.** Strip secrets, tokens and personal data from anything you paste, save or hand on.
2. **Build a tight feedback loop** that shows the failure in seconds. Prefer, in this order: a failing test at the seam that reaches the bug; a curl or HTTP script against the dev server; a CLI run with a fixture and a diff of the output; a headless browser script (Playwright, as `web_balance.js` does) asserting on DOM, console or network; a replay of a captured request or event log; a throwaway harness around one function; a fuzz loop for "sometimes wrong"; a bisection harness (`git bisect run`) when it broke between two known states; a differential run of old against new. A human clicking is the last resort, and then guide the person with a script so the loop stays structured. For non-deterministic bugs, raise the failure rate until the loop is reliable. If you genuinely cannot build a loop, say so and ask for the one thing you need.
3. **Reproduce and minimise** until the smallest input or setup still fails.
4. **Hypothesise.** Write 3 to 5 ranked, falsifiable hypotheses and the prediction each makes before you test any.
5. **Instrument one hypothesis at a time.** A debugger or REPL breakpoint beats ten logs; targeted logs at the boundaries that separate hypotheses; never "log everything and grep".
6. **Fix with a regression test.** Turn the minimal repro into a failing test, watch it fail (if you forced the red by mutating code, diff against a pristine copy to prove the mutation landed), apply the fix, watch it pass, re-run the original scenario.
7. **Clean up.** Remove instrumentation and throwaway harnesses, and say what the root cause was.
