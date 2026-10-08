# Obsidian Local REST API — Full Endpoint Reference

Base URL: `https://127.0.0.1:27124` (HTTPS) or `http://127.0.0.1:27123` (HTTP, disabled by default)

All endpoints except `GET /` require:
```
Authorization: Bearer <API_KEY>
```

---

## 1. Server Status

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | `/` | No | Returns server status and authentication info |

Response fields: `status`, `service`, `versions`, `authenticated`.

---

## 2. Vault File Operations

### Read a File
```
GET /vault/{filePath}
```
- `filePath`: Relative path from vault root, e.g., `Claude-Memory/Context/Project.md`
- Default response: raw Markdown text
- Add header `Accept: application/vnd.olrapi.note+json` to get structured JSON with frontmatter, tags, stat, path, content

### Append to a File
```
POST /vault/{filePath}
```
- Appends content to the end of the file
- Creates the file if it does not exist
- Body: Markdown text (`Content-Type: text/markdown`)

### Create or Replace a File
```
PUT /vault/{filePath}
```
- Overwrites the entire file, or creates it if it does not exist
- Body: Markdown text (`Content-Type: text/markdown`)

### Surgical Patch
```
PATCH /vault/{filePath}
```
Headers:
| Header | Values | Description |
|---|---|---|
| `Operation` | `append`, `prepend`, `replace` | What to do with the content |
| `Target-Type` | `heading`, `block`, `frontmatter` | Type of target element |
| `Target` | e.g., `## Summary` or `status` | The specific heading, block ref, or frontmatter key |
| `Content-Type` | `text/markdown` or `application/json` | Content format |

Examples:
- Append under heading `## Log`: `Target-Type: heading`, `Target: Log`
- Update frontmatter field `status`: `Target-Type: frontmatter`, `Target: status`, body: `"done"` (JSON string)
- Append after block reference `^abc123`: `Target-Type: block`, `Target: ^abc123`

### Delete a File
```
DELETE /vault/{filePath}
```

---

## 3. Directory Listing

### List Root
```
GET /vault/
```
Returns array of filenames and directory names. Directory names end with `/`.

### List a Subdirectory
```
GET /vault/{directoryPath}/
```
Note the trailing slash. Empty directories are not returned.

---

## 4. Active File

| Method | Endpoint | Description |
|---|---|---|
| GET | `/active/` | Read the currently open file in Obsidian |
| POST | `/active/` | Append to the currently open file |
| PUT | `/active/` | Replace content of the currently open file |
| PATCH | `/active/` | Surgical patch on the currently open file (same headers as vault PATCH) |
| DELETE | `/active/` | Delete the currently open file |

---

## 5. Periodic Notes

Supports: `daily`, `weekly`, `monthly`, `quarterly`, `yearly`

### Current Period
```
GET    /periodic/{period}/       # Read current period note
POST   /periodic/{period}/       # Append to current period note
PUT    /periodic/{period}/       # Replace current period note
PATCH  /periodic/{period}/       # Surgical patch
DELETE /periodic/{period}/       # Delete
```

### Specific Date
```
GET    /periodic/{period}/{date}  # date format: YYYY-MM-DD
POST   /periodic/{period}/{date}
PUT    /periodic/{period}/{date}
PATCH  /periodic/{period}/{date}
DELETE /periodic/{period}/{date}
```

---

## 6. Search

### Simple Full-Text Search
```
POST /search/simple/?query={terms}
```
- Uses Obsidian's built-in fuzzy search
- Returns: `[ { filename, score, matches: [ { context, match: { start, end } } ] } ]`

### Advanced Search
```
POST /search/
```

**Dataview DQL** (requires Dataview plugin installed):
```
Content-Type: application/vnd.olrapi.dataview.dql+txt

TABLE file.name, status FROM "Claude-Memory" WHERE contains(tags, "claude-memory")
```

**JsonLogic** (metadata filter on frontmatter, tags, path):
```
Content-Type: application/vnd.olrapi.jsonlogic+json

{ "and": [{ "in": ["claude-memory", { "var": "tags" }] }, { ">": [{ "var": "stat.mtime" }, 1700000000000] }] }
```

---

## 7. Tags

```
GET /tags/
```
Returns all tags across the vault with usage counts: `{ "tag-name": count, ... }`

---

## 8. Commands

### List Commands
```
GET /commands/
```
Returns: `[ { id, name } ]` for all available Obsidian commands.

### Execute a Command
```
POST /commands/{commandId}/
```
Triggers the command as if run from the command palette.

Example: Open the Graph View
```
POST /commands/graph:open/
```

---

## Response Schemas

### Note JSON Format (Accept: application/vnd.olrapi.note+json)
```json
{
  "path": "Claude-Memory/Context/topic.md",
  "content": "# Title\n\nBody text...",
  "frontmatter": { "tags": ["claude-memory"], "created": "2026-04-11" },
  "tags": ["#claude-memory"],
  "stat": { "ctime": 1712800000000, "mtime": 1712850000000, "size": 1024 }
}
```

### Error Format
```json
{
  "errorCode": 40401,
  "message": "File does not exist"
}
```

Common error codes:
- `40401` — File not found
- `40101` — Unauthorized (bad API key)
- `40901` — Conflict (file locked)

---

## Port Reference

| Port | Protocol | Default State |
|---|---|---|
| 27124 | HTTPS (self-signed cert) | Enabled |
| 27123 | HTTP | Disabled |

To avoid certificate warnings in scripts:
- `curl -k` (skip verification, safe for localhost)
- Python: `requests.get(url, verify=False)`
- Node.js: `https.globalAgent.options.rejectUnauthorized = false`
