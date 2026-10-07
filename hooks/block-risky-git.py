#!/usr/bin/env python3
"""PreToolUse hook (Bash): blocks the git commands that break the team's rules or cannot be undone.
Reads the hook JSON on stdin; exit 2 with a message on stderr blocks the command, exit 0 allows it.
Normal `git push` stays allowed. A person can still run a blocked command themselves (the ! prefix in Claude Code)."""
import json, re, shlex, sys

def segments(cmd):
    return [s for s in re.split(r"&&|\|\||;|\n|\|", cmd) if s.strip()]

def git_args(seg):
    try: t = shlex.split(seg, posix=True)
    except ValueError: return None
    while t and re.fullmatch(r"[A-Za-z_]\w*=.*", t[0]): t = t[1:]  # leading VAR=value
    if not t or t[0] != "git": return None
    t = t[1:]
    while t and t[0].startswith("-"):  # global options: -C path, -c k=v, --git-dir=...
        t = t[2:] if t[0] in ("-C", "-c") else t[1:]
    return t

def verdict(t):
    if not t: return None
    sub, a = t[0], t[1:]
    flags = [x for x in a if x.startswith("-")]
    short = lambda ch: any(re.fullmatch(r"-[A-Za-z]+", f) and ch in f[1:] for f in flags)
    if sub == "add" and ("--all" in a or "-u" in a or "--update" in a or short("A") or "." in a or ":/" in a):
        return "git add -A / . / -u sweeps in files other sessions changed. Name the files you changed: git add path1 path2"
    if sub == "commit" and ("--all" in a or short("a")):
        return "git commit -a commits every tracked change. Stage the files you changed by name, then commit"
    if sub == "reset" and "--hard" in a: return "git reset --hard deletes uncommitted work and cannot be undone"
    if sub == "clean" and (short("f") or "--force" in a) and not short("n") and "--dry-run" not in a:
        return "git clean -f deletes untracked files for good"
    if sub in ("checkout", "restore") and ("." in a or ":/" in a): return f"git {sub} . throws away every uncommitted change"
    if sub == "branch" and ("-D" in a or ("--delete" in a and "--force" in a) or short("D")): return "git branch -D deletes a branch even if unmerged"
    if sub == "push" and ("--force" in a or "-f" in a or any(x.startswith("+") and len(x) > 1 for x in a)):
        return "force push rewrites remote history (--force-with-lease is allowed)"
    return None

def check(cmd):
    for seg in segments(cmd):
        v = verdict(git_args(seg))
        if v: return v
    return None

if __name__ == "__main__":
    try: cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except Exception: sys.exit(0)  # never block on a malformed hook payload
    v = check(cmd)
    if v:
        sys.stderr.write(f"Blocked by the Adams git guardrail: {v}. Ask the user to run it themselves if it is really needed.\n")
        sys.exit(2)
