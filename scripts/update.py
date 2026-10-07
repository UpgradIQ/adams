#!/usr/bin/env python3
"""Adams versions and updates.
  python3 update.py version            print the installed version
  python3 update.py update [--auto|--check]
        no flag: update to the newest release tag now
        --check: only report whether a newer release exists
        --auto : what the SessionStart hook runs: at most once a day, silent unless it updated, never fails
  python3 update.py notes X.Y.Z        print the CHANGELOG section of a version (used by the release workflow)
Updates follow release TAGS (vX.Y.Z), not the main branch, and only fast-forward a clean clone.
Opt out of the automatic check with ADAMS_AUTO_UPDATE=0."""
import json, os, re, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
HOME = os.path.expanduser("~")
TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")

def version(root=ROOT):
    try: return open(os.path.join(root, "VERSION"), encoding="utf-8").read().strip()
    except OSError: return "unknown"

def semver(v):
    m = re.match(r"v?(\d+)\.(\d+)\.(\d+)$", v or ""); return tuple(map(int, m.groups())) if m else (0, 0, 0)

def git(*a, timeout=25):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, timeout=timeout)

def latest_tag():
    tags = [t for t in git("tag", "--list", "v*").stdout.split() if TAG.match(t)]
    return max(tags, key=semver) if tags else None

def notes(ver, root=ROOT):
    """The CHANGELOG section for one version, without its heading."""
    text = open(os.path.join(root, "CHANGELOG.md"), encoding="utf-8").read()
    m = re.search(rf"^## {re.escape(ver)}\b[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else ""

def stamp_path(): return os.path.join(HOME, ".config", "adams", "update-check.json")

def throttled():
    try: return time.time() - json.load(open(stamp_path())).get("checked", 0) < 24 * 3600
    except (OSError, ValueError): return False

def touch_stamp():
    try:
        os.makedirs(os.path.dirname(stamp_path()), exist_ok=True)
        json.dump({"checked": time.time()}, open(stamp_path(), "w"))
    except OSError: pass

def update(mode):
    auto, check = mode == "--auto", mode == "--check"
    say = (lambda m: None) if auto else print
    if auto and os.environ.get("ADAMS_AUTO_UPDATE") == "0": return 0
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        say("Adams is installed as a Claude Code plugin: Claude Code updates it. Enable auto-update in /plugin, or run: claude plugin marketplace update adams"); return 0
    if auto and throttled(): return 0
    if auto: touch_stamp()
    try:
        if git("fetch", "--tags", "--quiet", "origin").returncode != 0: say("Could not reach the Adams repository; try again later."); return 0
    except Exception: say("Could not reach the Adams repository; try again later."); return 0
    cur, tag = version(), latest_tag()
    if not tag or semver(tag) <= semver(cur): say(f"Adams {cur} is up to date."); return 0
    if check: print(f"Adams {tag[1:]} is available (you have {cur}). Run: adams update"); return 0
    if git("status", "--porcelain", "--untracked-files=no").stdout.strip(): say(f"Adams {tag[1:]} is available, but this clone has uncommitted changes. Commit or stash them, then run: adams update"); return 0
    if git("merge-base", "--is-ancestor", "HEAD", tag).returncode != 0: say(f"Adams {tag[1:]} is available, but this clone has commits that are not in the release. Update it by hand."); return 0
    if git("merge", "--ff-only", "--quiet", tag).returncode != 0: say("Update failed (could not fast-forward)."); return 0
    new = version()
    print(f"Adams updated {cur} -> {new}.")
    body = notes(new)
    if body: print("What is new:\n" + "\n".join(body.split("\n")[:12]))
    subprocess.run([sys.executable, os.path.join(ROOT, "bin", "adams"), "install"], capture_output=True, text=True)  # registers hooks a new version may add
    print("Start a new session to load it.")
    return 0

if __name__ == "__main__":
    a = sys.argv[1:]; cmd = a[0] if a else "version"
    if cmd == "version": print(version())
    elif cmd == "update":
        try: sys.exit(update(a[1] if len(a) > 1 else ""))
        except Exception as e:
            if "--auto" not in a: raise
            sys.exit(0)  # the automatic check must never break a session
    elif cmd == "notes" and len(a) > 1: print(notes(a[1]))
    else: print(__doc__); sys.exit(2)
