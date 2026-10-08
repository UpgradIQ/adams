## 5. Retro: improve the environment after a bad session

Run when a session was slow, wrong or repetitive. You are improving the environment for future runs, not blaming the session. Read the primary source (the session log or this conversation), then look for:

- **Navigation:** time spent finding a file or fact; add a pointer to the router or a guide.
- **Automated checks:** an error a lint, test or `check.py` rule could have caught; add the rule.
- **Steering size:** instructions in `CLAUDE.md`, `ALWAYS.md` or a guide that are huge, duplicated or change nothing; move them to a guide or delete them.
- **Tool economy:** expensive calls that a script or a smaller query would replace.
- **Information access:** a fact the agent needed and could not see (logs, a live URL, a read-only account); give it access.

Present candidates to the owner by severity. Accepted fixes go into the Adams repo in the same task, then `scripts/selftest.py` (the standing rule: a correction becomes a rule, fixed everywhere).
