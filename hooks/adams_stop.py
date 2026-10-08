#!/usr/bin/env python3
"""Stop hook: runs the Adams text checks on the .md and .txt files changed in the working repo and blocks the stop when they are flagged.
Files that passed are remembered by content hash, so only edits are checked again. Never fails a session: any error exits 0 silently."""
import hashlib, json, os, subprocess, sys, tempfile

SKIP = {"node_modules", ".git", ".planning"}
sha1 = lambda b: hashlib.sha1(b).hexdigest()

def changed_text_files(cwd):
    r = subprocess.run(["git", "status", "--porcelain", "-z", "-uall"], cwd=cwd, capture_output=True, text=True, timeout=20)
    if r.returncode: return []
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True, timeout=20).stdout.strip()
    out, parts = [], r.stdout.split("\0")
    i = 0
    while i < len(parts):
        e = parts[i]; i += 1
        if len(e) < 4: continue
        if e[0] in "RC": i += 1  # rename or copy: the next field is the old path
        p = e[3:]
        if p.lower().endswith((".md", ".txt")) and not SKIP & set(p.split("/")) and "D" not in e[:2] and os.path.isfile(os.path.join(top, p)):
            out.append(os.path.join(top, p))
    return out

def main():
    try: data = json.load(sys.stdin)
    except Exception: data = {}
    if data.get("stop_hook_active") or os.environ.get("ADAMS_STOP") == "0": return  # ADAMS_STOP=0 opts out
    cwd = data.get("cwd") or os.getcwd()
    files = changed_text_files(cwd)
    state = os.path.join(tempfile.gettempdir(), "adams-stop-" + sha1(cwd.encode()) + ".json")
    try: seen = set(json.load(open(state)))
    except Exception: seen = set()
    hashes = {f: sha1(open(f, "rb").read()) for f in files}
    todo = [f for f in files if hashes[f] not in seen]
    if not todo: return
    check = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "check.py")
    r = subprocess.run([sys.executable, check, *todo], cwd=cwd, capture_output=True, text=True, timeout=60)
    out = r.stdout + r.stderr
    if "FLAGGED" in out:
        tail = "\n".join(out.strip().splitlines()[-15:])
        print(json.dumps({"decision": "block", "reason": "Adams check flagged the changed text files. Fix every BLOCK hit, re-run `adams check <files>`, then finish.\n" + tail}))
    elif r.returncode == 0:
        json.dump(sorted(seen | {hashes[f] for f in todo}), open(state, "w"))

if __name__ == "__main__":
    try: main()
    except Exception: pass
    sys.exit(0)
