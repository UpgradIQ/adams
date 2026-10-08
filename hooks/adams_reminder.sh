#!/bin/sh
# UserPromptSubmit hook: stdout is added to the model's context on every prompt.
cat <<'X'
Adams auto-run is ON. Align first: on any non-trivial task (or when work drifts) read the project docs, ask the open decisions in one round (max 4), each with your recommended best practice and why, and record the answers before building; skip for small, reversible tasks (modules/workflow/GUIDE.md section 1). Think like a senior owner: read the intent, not the literal words; recommend the best option with reasons; truth over wishes. If the task writes text, builds or changes a deck, PDF, doc, image, web page, UI or dashboard, or has Arabic: call the `adams` skill first (`adams:adams` as a plugin), run `adams check FILE_OR_URL` on the result before reporting, and state the results.
X
