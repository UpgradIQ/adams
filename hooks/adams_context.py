#!/usr/bin/env python3
"""SessionStart hook: reloads the project's settled decisions (.adams/decisions.md) into context after a start, restart or compaction.
Silent when the file is absent. Never fails a session."""
import json, os, sys

try:
    cwd = (json.load(sys.stdin).get("cwd")) or os.getcwd()
    lines = open(os.path.join(cwd, ".adams", "decisions.md"), encoding="utf-8").read().splitlines()[-80:]
    print("Adams: settled decisions for this project (from .adams/decisions.md). Keep to them; if the work must deviate, stop and ask first.\n" + "\n".join(lines))
except Exception: pass
sys.exit(0)
