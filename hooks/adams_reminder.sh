#!/bin/sh
# UserPromptSubmit hook: stdout is added to the model's context. Prints once per session (marker keyed by session_id); without a session_id it prints every time.
id=$(sed -n 's/.*"session_id" *: *"\([A-Za-z0-9_-]*\)".*/\1/p' | head -n 1)
if [ -n "$id" ]; then
  m="${TMPDIR:-/tmp}/adams-reminder-$id"
  [ -e "$m" ] && exit 0
  : > "$m"
fi
cat <<'X'
Adams auto-run is ON. Align first: on any non-trivial task or drift, read the project docs, ask the open decisions in one round (max 4), each with your recommended best practice and why; skip for small, reversible tasks. If the task writes text, builds or changes a deck, PDF, doc, image, web page, UI or dashboard, or has Arabic: call the `adams` skill first (`adams:adams` as a plugin), run `adams check FILE_OR_URL` on the result and state it.
X
