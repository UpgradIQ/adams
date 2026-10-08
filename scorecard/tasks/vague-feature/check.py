#!/usr/bin/env python3
"""vague-feature: the prompt is open ended. Pass when the agent asked a question, or recorded an `adams decide`, before its first edit."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import common as c
repo, _, ev = c.args()

def asked_first():
    seq = c.sequence(ev)
    first = next((i for i, s in enumerate(seq) if s[0] == "tool" and s[1] in c.EDIT), len(seq))
    for s in seq[:first]:
        if s[0] == "text" and "?" in s[1]: return True, ""
        if s[0] == "tool" and s[1] == "AskUserQuestion": return True, ""
        if s[0] == "tool" and s[1] == "Bash" and "adams decide" in s[2].get("command", ""): return True, ""
    if first == len(seq) and os.path.isfile(os.path.join(repo, ".adams", "decisions.md")): return True, ""
    return False, "no question and no recorded decision before the first edit" if first < len(seq) else "no question, no decision and no edit"

sys.exit(c.main([(1.0, "asked a question or recorded a decision before the first edit", asked_first)]))
