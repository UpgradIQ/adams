#!/usr/bin/env python3
"""Stop hook: runs the Adams text checks on the .md and .txt files changed in the working repo, and checks that code changed in this session was verified
(see adams_gates.py). Blocks the stop once when either fails. Files that passed the text check are remembered by content hash, so only edits are checked again.
Never fails a session: any error exits 0 silently."""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adams_gates as g

SKIP = {"node_modules", ".git", ".planning", ".adams"}
sha1 = g.sha1

def changed_text_files(cwd):
    top, paths = g.changed_paths(cwd)
    return [os.path.join(top, p) for p in paths if p.lower().endswith((".md", ".txt")) and not SKIP & set(p.split("/"))]

def text_reason(cwd):
    files = changed_text_files(cwd)
    state = os.path.join(tempfile.gettempdir(), "adams-stop-" + sha1(cwd.encode()) + ".json")
    try: seen = set(json.load(open(state)))
    except Exception: seen = set()
    hashes = {f: sha1(open(f, "rb").read()) for f in files}
    todo = [f for f in files if hashes[f] not in seen]
    if not todo: return None
    check = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "check.py")
    r = subprocess.run([sys.executable, check, *todo], cwd=cwd, capture_output=True, text=True, timeout=60)
    out = r.stdout + r.stderr
    if "FLAGGED" in out:
        tail = "\n".join(out.strip().splitlines()[-15:])
        return "Adams check flagged the changed text files. Fix every BLOCK hit, re-run `adams check <files>`, then finish.\n" + tail
    if r.returncode == 0: json.dump(sorted(seen | {hashes[f] for f in todo}), open(state, "w"))

def verify_reason(data):
    """Code this session edited (the align gate recorded the tree before its first edit) changed since the last green verification."""
    if g.verify_off(): return None
    base = g.load(g.state_path("align", data.get("session_id"), data.get("cwd") or os.getcwd()), {}).get("base") or {}
    for top, before in base.items():
        if not g.source_files(g.changed_paths(top)[1]) or g.tree_hash(top) == before: continue
        cmds = g.needs_verify(top, data.get("session_id"), data.get("cwd") or os.getcwd())
        if cmds: return "Code changed since the last green verification. Run " + ", ".join(cmds) + ", fix failures, and quote the results. Override: the user sets ADAMS_VERIFY=0."
    return None

def main():
    try: data = json.load(sys.stdin)
    except Exception: data = {}
    if data.get("stop_hook_active"): return
    reasons = []
    if os.environ.get("ADAMS_STOP") != "0":  # ADAMS_STOP=0 opts out of the text check
        try: reasons.append(text_reason(data.get("cwd") or os.getcwd()))
        except Exception: pass
    try: reasons.append(verify_reason(data))
    except Exception: pass
    reasons = [r for r in reasons if r]
    if reasons: print(json.dumps({"decision": "block", "reason": "\n\n".join(reasons)}))

if __name__ == "__main__":
    try: main()
    except Exception: pass
    sys.exit(0)
