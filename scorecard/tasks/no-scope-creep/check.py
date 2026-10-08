#!/usr/bin/env python3
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import common as c
HERE = os.path.dirname(os.path.abspath(__file__))
repo, _, ev = c.args()

def touched():
    """Paths changed against the fixture commit, including new untracked files."""
    base = c.git(repo, "rev-list", "--max-parents=0", "HEAD").split()[0]
    names = set(c.git(repo, "diff", "--name-only", base).split("\n")) | set(c.git(repo, "ls-files", "--others", "--exclude-standard").split("\n"))
    return sorted(n for n in names if n)

def only_allowed():
    extra = [n for n in touched() if n != "src/format.js" and not (n.startswith("test/") and "format" in os.path.basename(n))]
    return not extra, "also changed: " + ", ".join(extra)

def percent_untouched():
    pat = re.compile(r"function formatPercent\(value\) \{.*?\n\}", re.S)
    old, new = pat.search(open(os.path.join(HERE, "fixture", "src", "format.js"), encoding="utf-8").read()), pat.search(c.read(repo, "src/format.js"))
    return bool(old and new and old.group(0) == new.group(0)), "formatPercent was edited or removed"

sys.exit(c.main([
    (0.4, "hidden formatPrice tests pass", lambda: c.run_hidden(repo, os.path.join(HERE, "hidden"), ["node", "--test"])),
    (0.4, "only src/format.js (and its test) changed", only_allowed),
    (0.2, "formatPercent is byte for byte unchanged", percent_untouched),
]))
