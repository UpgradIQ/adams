#!/usr/bin/env python3
"""Stop hook: runs the Adams text checks on the .md and .txt files this session wrote, and checks that code this session wrote was verified
(see adams_gates.py). "This session wrote" is the touched list that adams_verify_record.py keeps per session_id; files other sessions changed in the same folder
are never checked or reported, and a stop without a session_id or a touched list never blocks. Blocks the stop once when either check fails.
Files that passed the text check are remembered by content hash, so only edits are checked again. Never fails a session: any error exits 0 silently."""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adams_gates as g

SKIP = {"node_modules", ".git", ".planning", ".adams"}
sha1 = g.sha1

def changed_text_files(cwd):
    top, paths = g.changed_paths(cwd)
    return [os.path.join(top, p) for p in paths if p.lower().endswith((".md", ".txt")) and not SKIP & set(p.split("/"))]

def text_reason(cwd, mine):
    files = [f for f in changed_text_files(cwd) if f in mine]
    if not files: return None
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

def verify_reason(data, mine):
    """Source files this session wrote changed since the last green verification."""
    if g.verify_off(): return None
    tops = {}
    for p in mine:
        d = os.path.dirname(p)
        if d not in tops: tops[d] = g.git_top(d)
    for top in {t for t in tops.values() if t}:
        if not {os.path.join(top, r) for r in g.source_files(g.changed_paths(top)[1])} & mine: continue
        cmds = g.needs_verify(top, data.get("session_id"), data.get("cwd") or os.getcwd())
        if cmds: return "Code changed since the last green verification. Run " + ", ".join(cmds) + ", fix failures, and quote the results. Override: the user sets ADAMS_VERIFY=0."
    return None

def main():
    try: data = json.load(sys.stdin)
    except Exception: data = {}
    if data.get("stop_hook_active"): return
    mine = g.touched(data.get("session_id"))
    if not mine: return
    reasons = []
    if os.environ.get("ADAMS_STOP") != "0":  # ADAMS_STOP=0 opts out of the text check
        try: reasons.append(text_reason(data.get("cwd") or os.getcwd(), mine))
        except Exception: pass
    try: reasons.append(verify_reason(data, mine))
    except Exception: pass
    reasons = [r for r in reasons if r]
    if reasons: print(json.dumps({"decision": "block", "reason": "\n\n".join(reasons)}))

if __name__ == "__main__":
    try: main()
    except Exception: pass
    sys.exit(0)
