"""Shared helpers for the scorecard checks: parse a stream-json transcript, run hidden tests, print a score.
Every tasks/<name>/check.py calls main(criteria): exit 0 when all criteria pass, 1 otherwise, 2 when it cannot run.
A criterion is (weight, label, fn); fn returns True/False or (bool, detail)."""
import json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def events(path):
    out = []
    try: lines = open(path, encoding="utf-8").read().splitlines()
    except OSError: return out
    for l in lines:
        try: out.append(json.loads(l))
        except ValueError: pass
    return out

def blocks(evs, role, kind):
    """Content blocks of one kind ('text', 'tool_use', 'tool_result') from the assistant or user messages, in order."""
    for e in evs:
        m = e.get("message")
        if e.get("type") == role and isinstance(m, dict) and isinstance(m.get("content"), list):
            for b in m["content"]:
                if isinstance(b, dict) and b.get("type") == kind: yield b

def sequence(evs):
    """The assistant's blocks in order: ("text", str) or ("tool", name, input)."""
    out = []
    for e in evs:
        m = e.get("message")
        if e.get("type") == "assistant" and isinstance(m, dict) and isinstance(m.get("content"), list):
            for b in m["content"]:
                if isinstance(b, dict) and b.get("type") == "text": out.append(("text", b.get("text", "")))
                elif isinstance(b, dict) and b.get("type") == "tool_use": out.append(("tool", b.get("name", ""), b.get("input") or {}))
    return out

def tools(evs):
    """[(name, input)] for every tool call, in order."""
    return [(b.get("name", ""), b.get("input") or {}) for b in blocks(evs, "assistant", "tool_use")]

def final_text(evs):
    for e in reversed(evs):
        if e.get("type") == "result" and isinstance(e.get("result"), str): return e["result"]
    texts = [b.get("text", "") for b in blocks(evs, "assistant", "text")]
    return texts[-1] if texts else ""

def results(evs):
    """{tool_use_id: (output text, is_error)}"""
    out = {}
    for b in blocks(evs, "user", "tool_result"):
        c = b.get("content")
        out[b.get("tool_use_id")] = ("\n".join(x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else str(c or ""), bool(b.get("is_error")))
    return out

EDIT = ("Edit", "Write", "MultiEdit", "NotebookEdit")
def edit_path(name, inp): return inp.get("file_path") or inp.get("notebook_path") or ""

def git(repo, *a):
    return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True).stdout

def read(repo, rel):
    try: return open(os.path.join(repo, rel), encoding="utf-8").read()
    except OSError: return ""

def run_hidden(repo, hidden_dir, cmd, env=None):
    """Copy the repo (without .git) to a temp folder, add the hidden tests on top, run cmd there. Returns (passed, output tail)."""
    t = tempfile.mkdtemp(prefix="scorecard-hidden-")
    try:
        dst = os.path.join(t, "repo")
        shutil.copytree(repo, dst, ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
        shutil.copytree(hidden_dir, dst, dirs_exist_ok=True)
        r = subprocess.run(cmd, cwd=dst, capture_output=True, text=True, timeout=120, env={**os.environ, "PYTHONPATH": dst, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})})
        return r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]
    except subprocess.TimeoutExpired: return False, "timed out"
    finally: shutil.rmtree(t, ignore_errors=True)

def args():
    """(repo, transcript, events) from the command line: check.py REPO TRANSCRIPT."""
    if len(sys.argv) < 3: print("usage: check.py REPO TRANSCRIPT"); sys.exit(2)
    return sys.argv[1], sys.argv[2], events(sys.argv[2])

def main(criteria):
    got = total = 0.0
    for weight, label, fn in criteria:
        try: res = fn()
        except Exception as e: res = (False, f"check error: {e}")
        ok, detail = res if isinstance(res, tuple) else (res, "")
        if ok == "skip": print(f"SKIP {label}: {detail}"); return 2
        total += weight; got += weight if ok else 0
        print(f"{'ok  ' if ok else 'FAIL'} {label}" + (f": {detail}" if detail and not ok else ""))
    print(f"SCORE {got / total:.2f}")
    return 0 if got >= total - 1e-9 else 1
