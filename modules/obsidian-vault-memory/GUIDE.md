# Obsidian Vault Memory Skill

Enables Claude to use a local Obsidian vault as persistent, queryable memory via the **Local REST API plugin** (by coddingtonbear). Claude can read, write, search, and patch notes surgically without disrupting existing content.

---

## Prerequisites

The user must have:
1. **Obsidian** installed and running on their device.
2. **Local REST API plugin** installed and enabled (Settings > Community Plugins > Local REST API).
3. The **API key** from: Settings > Local REST API.
4. Default port: `27124` (HTTPS). HTTP port: `27123` (optional, disabled by default).

> Ask the user to confirm their API key and vault name before the first operation. Store them in the conversation for the session.

---

## Connection Pattern

All requests go to:
```
https://127.0.0.1:27124/<endpoint>
Authorization: Bearer <API_KEY>
```

SSL note: The plugin uses a self-signed certificate. When calling from within an artifact or script, use `-k` (curl) or `rejectUnauthorized: false` (Node.js) or `verify=False` (Python requests). This is safe because the connection is local-only.

**Test connectivity first:**
```bash
curl -k -s -H "Authorization: Bearer <API_KEY>" https://127.0.0.1:27124/
```
A successful response returns server status JSON. If it fails, Obsidian is not running or the plugin is not enabled.

---

## Core API Endpoints

See `references/endpoints.md` for the full reference table. The most frequently used operations are:

| Operation | Method | Endpoint |
|---|---|---|
| Read a note | GET | `/vault/{path}` |
| Create or replace a note | PUT | `/vault/{path}` |
| Append to a note | POST | `/vault/{path}` |
| Surgical patch (heading/frontmatter) | PATCH | `/vault/{path}` |
| Delete a note | DELETE | `/vault/{path}` |
| List files in a directory | GET | `/vault/{directory}/` |
| Full-text search | POST | `/search/simple/?query={terms}` |
| Get/create today's daily note | GET/POST | `/periodic/daily/` |
| List all tags | GET | `/tags/` |
| Execute an Obsidian command | POST | `/commands/{commandId}/` |
| Get active file | GET | `/active/` |

---

## Vault Structure Convention

When setting up the vault as Claude's memory, create this folder structure:

```
vault-root/
├── Claude-Memory/
│   ├── README.md              # Index + instructions
│   ├── Context/               # Per-topic persistent context
│   │   └── {topic}.md
│   ├── Sessions/              # Per-session logs (dated)
│   │   └── YYYY-MM-DD.md
│   ├── Projects/              # Project-specific notes
│   │   └── {project-name}.md
│   └── Quick-Capture/         # Rapid unsorted entries
│       └── inbox.md
```

Use frontmatter on every Claude-created note:
```yaml
---
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [claude-memory, {topic}]
source: claude
---
```

---

## Standard Workflows

### 1. Save Information to Vault

**Append to an existing note** (preferred — non-destructive):
```bash
curl -k -X POST \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: text/markdown" \
  --data "## Entry — YYYY-MM-DD\n\n{content}\n\n---\n" \
  "https://127.0.0.1:27124/vault/Claude-Memory/Context/{topic}.md"
```

**Create a new note** (PUT overwrites; use only for new files):
```bash
curl -k -X PUT \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: text/markdown" \
  --data "---\ncreated: YYYY-MM-DD\ntags: [claude-memory]\n---\n\n{content}" \
  "https://127.0.0.1:27124/vault/Claude-Memory/{path}.md"
```

### 2. Read a Note

```bash
curl -k -H "Authorization: Bearer <API_KEY>" \
  "https://127.0.0.1:27124/vault/Claude-Memory/Context/{topic}.md"
```

Response is raw Markdown text.

### 3. Search the Vault

```bash
curl -k -X POST \
  -H "Authorization: Bearer <API_KEY>" \
  "https://127.0.0.1:27124/search/simple/?query={search+terms}"
```

Returns: array of `{ filename, score, matches[] }` objects.

### 4. Surgical Patch (append under a heading)

```bash
curl -k -X PATCH \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Operation: append" \
  -H "Target-Type: heading" \
  -H "Target: {Heading Name}" \
  -H "Content-Type: text/markdown" \
  --data "{content to append}" \
  "https://127.0.0.1:27124/vault/Claude-Memory/{note}.md"
```

Operations: `append`, `prepend`, `replace`.
Target-Type options: `heading`, `block`, `frontmatter`.

### 5. Today's Daily Note

```bash
# Read
curl -k -H "Authorization: Bearer <API_KEY>" \
  "https://127.0.0.1:27124/periodic/daily/"

# Append
curl -k -X POST \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: text/markdown" \
  --data "{content}" \
  "https://127.0.0.1:27124/periodic/daily/"
```

---

## Error Handling

| HTTP Code | Meaning | Action |
|---|---|---|
| 200 / 204 | Success | Proceed |
| 401 | Bad API key | Ask user to check plugin settings |
| 404 | File not found | Use PUT to create it first |
| 409 | Conflict | File may be open/locked in Obsidian |
| 000 / Connection refused | Obsidian not running or plugin off | Ask user to open Obsidian and enable plugin |

Always check for a `x-deny-reason` response header if the network proxy blocks the request.

---

## Session Workflow for Claude

When the user wants to use the vault as memory in a conversation:

1. **Session Start** — Ask for API key (once per session). Test connectivity with `GET /`.
2. **On "remember this"** — Identify the best target note/heading. Append; never overwrite unless explicitly asked.
3. **On "recall X"** — Search vault with `POST /search/simple/`. Read the top match. Summarize to the user.
4. **On "log to daily note"** — Append to `GET/POST /periodic/daily/`.
5. **On "update my project note"** — PATCH the relevant heading in the Projects folder.
6. **Session End** — Optionally write a session summary to `Claude-Memory/Sessions/YYYY-MM-DD.md`.

> Never delete user notes unless the user explicitly says "delete this note." Prefer append and patch over replace.

---

## Setup Checklist (First Use)

- [ ] Obsidian is installed and a vault is open.
- [ ] Local REST API plugin is installed and enabled.
- [ ] API key is copied from Settings > Local REST API.
- [ ] Port confirmed (default: 27124 HTTPS, or 27123 HTTP).
- [ ] Test request returns status 200.
- [ ] `Claude-Memory/` folder created in vault (Claude can do this via PUT).
- [ ] `Claude-Memory/README.md` created as the index note.

---

## Reference Files

- `references/endpoints.md` — Full endpoint table with all parameters and response schemas.
- `references/setup-guide.md` — Step-by-step plugin installation and first-use instructions for the user.
