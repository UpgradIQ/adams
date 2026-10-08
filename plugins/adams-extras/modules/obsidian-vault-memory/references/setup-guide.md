# Obsidian Vault Memory — First-Use Setup Guide

## Step 1: Install the Local REST API Plugin

1. Open Obsidian.
2. Go to **Settings > Community Plugins**.
3. Disable Safe Mode if prompted.
4. Click **Browse** and search for **Local REST API**.
5. Install and **Enable** it.

## Step 2: Get Your API Key

1. Go to **Settings > Local REST API**.
2. Copy the **API Key** shown. Keep it private — treat it like a password.
3. Note the **port** (default: 27124 for HTTPS).

## Step 3: Confirm Obsidian is Running

The plugin only works while Obsidian is open on your device. It runs a local server at:
```
https://127.0.0.1:27124
```

To test: open a browser and go to `https://127.0.0.1:27124/`. Accept the certificate warning. You should see a JSON status response.

## Step 4: Tell Claude Your API Key

At the start of your session, tell Claude:
> "My Obsidian API key is `<your-key>` and the port is 27124."

Claude will test the connection and confirm before doing anything.

## Step 5: Initialize the Memory Vault

Claude will create a `Claude-Memory/` folder in your vault with this structure:

```
Claude-Memory/
├── README.md              # Index + instructions
├── Context/               # Persistent topic notes
├── Sessions/              # Session logs by date
├── Projects/              # Project-specific notes
└── Quick-Capture/
    └── inbox.md           # Rapid capture
```

You can modify this structure at any time. Just tell Claude where to store things.

## Troubleshooting

| Problem | Fix |
|---|---|
| Connection refused | Open Obsidian; check plugin is enabled |
| 401 Unauthorized | Re-copy API key from plugin settings |
| Certificate warning | Use `-k` in curl, or trust the cert from `https://127.0.0.1:27124/obsidian-local-rest-api-certificate.crt` |
| File not found (404) | Claude will create the file first using PUT |
| Port conflict | Change port in Settings > Local REST API |

## Privacy Notes

- All traffic stays on your device (127.0.0.1 = localhost only).
- Never expose the API port to the internet.
- The plugin uses a self-signed TLS certificate for local encryption.
- Your API key is session-scoped. Do not share it in public conversations.
