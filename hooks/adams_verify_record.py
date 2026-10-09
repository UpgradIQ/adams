#!/usr/bin/env python3
"""PostToolUse and PostToolUseFailure hook (Bash, Edit, Write, MultiEdit, NotebookEdit). Edit tools: appends the file path to this session's touched list (state file
adams-touched-<session_id>), which scopes the Stop checks to files this session wrote; nothing is recorded without a session_id. Bash: a write-like command (redirect, tee, sed -i, perl -pi, mv, a script
writing a file) adds the changed files it names to the same list, and each verification command (test, build, typecheck, lint) is recorded with its result and the working-tree fingerprint.
The Stop hook and the commit gate compare that fingerprint with the current tree. Claude Code sends PostToolUse for a command that succeeded and
PostToolUseFailure for one that failed, so success is read from the event name, an exit code field if present, and the interrupted flag; unknown means not ok.
Never fails a session: any error exits 0 silently."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adams_gates as g

def touch(sid, paths):
    sp = g.state_path("touched", sid)
    t = g.load(sp, [])
    new = [p for p in sorted(paths) if p not in t]
    if new: g.save(sp, t + new)

def main():
    d = json.load(sys.stdin)
    if d.get("tool_name") in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        ti, sid = d.get("tool_input") or {}, d.get("session_id")
        p = ti.get("file_path") or ti.get("notebook_path")
        if p and sid and not g.gates_off(): touch(sid, [os.path.realpath(os.path.join(d.get("cwd") or os.getcwd(), p))])
        return
    cmd = (d.get("tool_input") or {}).get("command") or ""
    if d.get("session_id") and not g.gates_off(): touch(d["session_id"], g.bash_written(cmd, d.get("cwd") or os.getcwd()))
    v = g.VERIFY.search(cmd)
    if g.gates_off() or not v: return
    cwd = d.get("cwd") or os.getcwd()
    top = g.git_top(g.cmd_base(cmd, cwd, v.start()))  # `cd repo && npm test` verifies the repo, not the session folder
    if not top: return
    r = d.get("tool_response")
    r = r if isinstance(r, dict) else {}
    code = next((r[k] for k in ("exit_code", "exitCode", "returncode", "code") if isinstance(r.get(k), int)), 0)
    ok = d.get("hook_event_name") == "PostToolUse" and not r.get("interrupted") and code == 0  # shortcut: `cmd || true` counts as green; add a stdout parse if it matters
    sp = g.state_path("verify", d.get("session_id"), cwd)
    g.save(sp, (g.load(sp, []) + [{"cmd": cmd[:200], "ok": ok, "time": time.time(), "tree_hash": g.tree_hash(top), "top": top}])[-20:])

if __name__ == "__main__":
    try: main()
    except Exception: pass
    sys.exit(0)
