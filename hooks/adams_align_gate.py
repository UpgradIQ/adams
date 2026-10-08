#!/usr/bin/env python3
"""PreToolUse hook (Edit, Write, MultiEdit, NotebookEdit): the first code edit of a session is denied until the work is aligned with the user.
Aligned means `adams decide` touched <repo>/.adams/decisions.md after the first gated call. Docs (.md, .txt), .adams, .planning, paths outside a git work tree
and the Claude scratchpad are never gated. Opt out with ADAMS_GATES=0. Never blocks on an internal error."""
import json, os, shutil, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adams_gates as g

def main():
    data = json.load(sys.stdin)
    if g.gates_off(): return
    ti = data.get("tool_input") or {}
    p = ti.get("file_path") or ti.get("notebook_path")
    if not p: return
    cwd = data.get("cwd") or os.getcwd()
    p = os.path.realpath(os.path.join(cwd, p))
    top = g.git_top(os.path.dirname(p))
    if not top or "/tmp/claude-" in p: return
    rel = os.path.relpath(p, top)
    if rel.startswith((".adams/", ".planning/")) or rel.lower().endswith((".md", ".txt")): return
    sp = g.state_path("align", data.get("session_id"), cwd)
    st = g.load(sp, {})
    st.setdefault("t0", time.time()); st.setdefault("ok", []); st.setdefault("base", {}).setdefault(top, g.tree_hash(top))  # base: the tree before this session's first code edit
    dm = os.path.join(top, ".adams", "decisions.md")
    if top in st["ok"] or (os.path.isfile(dm) and os.path.getmtime(dm) > st["t0"]):
        if top not in st["ok"]: st["ok"].append(top)
        g.save(sp, st); return
    g.save(sp, st)
    cmd = "adams" if shutil.which("adams") else f'python3 "{os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bin", "adams")}"'
    if os.path.realpath(cwd) != top: cmd = f'cd "{top}" && {cmd}'
    reason = (f'Align before editing code. Ask the user the open decisions now (use the question tool, max 4 questions, each with your recommended best practice), then record them with: {cmd} decide "<decision>". '
              f'For a clear, small, reversible task run: {cmd} decide --small "<the one assumption>" and continue. Override: the user sets ADAMS_GATES=0.')
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))

if __name__ == "__main__":
    try: main()
    except Exception: pass
    sys.exit(0)
