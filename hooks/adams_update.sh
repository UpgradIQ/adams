#!/bin/sh
# SessionStart hook: checks for a new Adams release at most once a day. Silent unless it updated. Never fails the session.
python3 "$(dirname "$0")/../scripts/update.py" update --auto 2>/dev/null || true
