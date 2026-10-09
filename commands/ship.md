---
description: Ship this session's work. Commits your files by name, pushes, opens the PR and merges every open PR of yours once the fast checks pass. Replies in two lines.
---

# Ship this session's work

The user has said go: ship the work of this session.

1. Run `adams ship all --session ${CLAUDE_SESSION_ID}`. If `adams` is not on the PATH, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ship.py" all --session ${CLAUDE_SESSION_ID}`. It waits for the fast checks, so it can take several minutes; let it finish. Progress goes to stderr, the result is the two lines `Shipped:` and `Left:`.
2. If it prints a line starting with `ASK files:` (exit 5), some changed files are not known to be this session's. Decide from what you did in this session, not from the file names:
   - files you wrote: rerun with `--mine path1,path2`;
   - files that belong to other work: rerun with `--leave`;
   - not sure about a file: ask the user one question with the question tool, then rerun.
   Never add a file you did not write.
3. If `Left:` names a high-risk PR (exit 4), ask the user one yes or no question with the question tool: list the files it touches and ask whether to merge. On yes, rerun the same command with `--yes`. On no, leave it.
4. If it prints `NOT SHIPPED` (you are on the base branch or a detached HEAD), `gh is not installed` or `gh is not signed in`, tell the user that one line and stop. Do not create branches, switch branches, or sign in for them.
5. Never use `--admin`, `--force` or `--no-verify`, never merge into a branch other than the base branch, never delete a branch. A refused merge or a failed check is reported, not worked around.
6. Reply in exactly two lines: the `Shipped:` line and the `Left:` line, as printed. When `Left:` is not `none`, say in the same line what you will do next or what you need from the user.

The setting `auto_merge` in `.adams/ship.json` does not block this command: `/ship` is the explicit go. It only applies to `adams ship PR`.
