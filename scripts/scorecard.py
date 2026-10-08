#!/usr/bin/env python3
"""Adams real-task scorecard: give an agent 8 small programming tasks in throwaway git repos, then score the result with hidden deterministic checks.
  scorecard.py --dry-run                         no model calls: every fixture builds, every check FAILS on the untouched fixture and PASSES on its golden solution
  scorecard.py --run [--tasks a,b] [--runs N] [--max-cost USD]
                                                 runs `claude -p` (your real ~/.claude config, so personal instructions and the installed plugin apply) and COSTS MONEY
Layout: scorecard/tasks/<name>/{prompt.md, fixture/, check.py} plus optional hidden/, untracked/, golden/, golden.json. See scorecard/README.md.
A fixture file or folder named dot-x is created as .x (so no .env file is ever committed here)."""
import json, os, re, shutil, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SC = os.path.join(ROOT, "scorecard")
TASKS = os.path.join(SC, "tasks")
CLAUDE = os.path.expanduser("~/.local/bin/claude")
TOOLS = "Read,Edit,Write,MultiEdit,Glob,Grep,Bash"  # the agent runs unattended: these tools, nothing else (no web, no MCP)
GIT_ENV = {"GIT_AUTHOR_NAME": "scorecard", "GIT_AUTHOR_EMAIL": "scorecard@example.test", "GIT_COMMITTER_NAME": "scorecard", "GIT_COMMITTER_EMAIL": "scorecard@example.test"}
CASE_LOW, CASE_HIGH = 0.15, 0.70  # observed cost per case in our evals, USD

def git(repo, *a): return subprocess.run(["git", "-c", "commit.gpgsign=false", *a], cwd=repo, capture_output=True, text=True, env={**os.environ, **GIT_ENV})

def names(): return sorted(d for d in os.listdir(TASKS) if os.path.isfile(os.path.join(TASKS, d, "check.py")))

def copy_tree(src, dst):
    """Copy src over dst; a path part named dot-x becomes .x."""
    for d, _, files in os.walk(src):
        for f in files:
            rel = os.path.relpath(os.path.join(d, f), src)
            out = os.path.join(dst, *[("." + p[4:] if p.startswith("dot-") else p) for p in rel.split(os.sep)])
            os.makedirs(os.path.dirname(out), exist_ok=True); shutil.copy2(os.path.join(d, f), out)

def build(task):
    """A temp git repo holding the fixture as one commit, plus the untracked files. Returns the repo path."""
    repo = tempfile.mkdtemp(prefix=f"scorecard-{task}-")
    copy_tree(os.path.join(TASKS, task, "fixture"), repo)
    git(repo, "init", "-q", "-b", "main"); git(repo, "add", "."); r = git(repo, "commit", "-qm", "fixture")
    if r.returncode: raise RuntimeError("fixture commit failed: " + r.stderr)
    if os.path.isdir(os.path.join(TASKS, task, "untracked")): copy_tree(os.path.join(TASKS, task, "untracked"), repo)
    return repo

def synth(golden, path):
    """Write a stream-json transcript from golden.json: steps are {"text"} or {"tool","input","output"[,"error"]}."""
    lines = [{"type": "system", "subtype": "init"}]
    for i, s in enumerate(golden.get("steps", [])):
        if "text" in s: lines.append({"type": "assistant", "message": {"content": [{"type": "text", "text": s["text"]}]}})
        else:
            lines.append({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": f"t{i}", "name": s["tool"], "input": s["input"]}]}})
            lines.append({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": f"t{i}", "content": s.get("output", ""), "is_error": bool(s.get("error"))}]}})
    lines.append({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "result": golden.get("final", "")})
    open(path, "w", encoding="utf-8").write("".join(json.dumps(x) + "\n" for x in lines))

def check(task, repo, transcript, env=None):
    """Run the task's check.py. Returns (exit code, score, output); exit 0 pass, 1 fail, 2 cannot run."""
    r = subprocess.run([sys.executable, os.path.join(TASKS, task, "check.py"), repo, transcript], capture_output=True, text=True, timeout=600, env={**os.environ, **(env or {})})
    out = (r.stdout + r.stderr).strip()
    m = re.findall(r"^SCORE ([\d.]+)$", out, re.M)
    return r.returncode, (float(m[-1]) if m else 0.0), out

def dry_run():
    env = {"ADAMS_AUTO_INSTALL": "0"}  # no downloads here; the ui-overflow check reports exit 2 when Playwright or Chromium is missing
    rows, bad, tmp = [], 0, tempfile.mkdtemp(prefix="scorecard-dry-")
    try:
        for t in names():
            row = {"task": t, "fixture": "FAIL", "untouched": "-", "golden": "-"}
            try:
                p = open(os.path.join(TASKS, t, "prompt.md"), encoding="utf-8").read()
                assert p.strip() and chr(0x2014) not in p and chr(0x2013) not in p, "prompt.md is empty or has a dash"
                empty = os.path.join(tmp, t + "-empty.jsonl"); open(empty, "w").close()
                repo = build(t); row["fixture"] = "ok"
                rc, score, out = check(t, repo, empty, env)
                row["untouched"] = f"skipped (exit 2)" if rc == 2 else f"fails ({score:.2f})" if rc == 1 else f"PASSES ({score:.2f})"
                if rc == 0: bad += 1; print(f"--- {t}: the check passes on the untouched fixture\n{out}")
                if rc not in (1, 2): bad += rc != 0
                g = os.path.join(TASKS, t, "golden")
                if os.path.isdir(g) or os.path.isfile(os.path.join(TASKS, t, "golden.json")):
                    gj = json.load(open(os.path.join(TASKS, t, "golden.json"))) if os.path.isfile(os.path.join(TASKS, t, "golden.json")) else {}
                    if os.path.isdir(g): copy_tree(g, repo)
                    if gj.get("commit"):
                        git(repo, "add", "--", *[os.path.relpath(os.path.join(d, f), g) for d, _, fs in os.walk(g) for f in fs]); git(repo, "commit", "-qm", gj["commit"])
                    tr = os.path.join(tmp, t + "-golden.jsonl"); synth(gj, tr)
                    rc, score, out = check(t, repo, tr, env)
                    row["golden"] = "skipped (exit 2)" if rc == 2 else f"passes ({score:.2f})" if rc == 0 else f"FAILS ({score:.2f})"
                    if rc not in (0, 2): bad += 1; print(f"--- {t}: the check fails on the golden solution\n{out}")
                shutil.rmtree(repo, ignore_errors=True)
            except Exception as e:
                bad += 1; print(f"--- {t}: {e}")
            rows.append(row)
    finally: shutil.rmtree(tmp, ignore_errors=True)
    w = max(len(r["task"]) for r in rows)
    print(f"{'task'.ljust(w)}  fixture  check on the untouched fixture  check on the golden solution")
    for r in rows: print(f"{r['task'].ljust(w)}  {r['fixture'].ljust(7)}  {r['untouched'].ljust(30)}  {r['golden']}")
    print(f"scorecard dry-run {'OK' if not bad else 'FAILED'} ({len(rows)} tasks, no model calls)")
    return 1 if bad else 0

def run(selected, runs, max_cost):
    claude = CLAUDE if os.path.exists(CLAUDE) else shutil.which("claude")
    if not claude: print("claude CLI not found (expected ~/.local/bin/claude)"); return 2
    n = len(selected) * runs
    print(f"{n} cases, estimated ${n * CASE_LOW:.2f} to ${n * CASE_HIGH:.2f} on your Claude account, capped at ${max_cost:.2f}. The agent runs unattended with: {TOOLS}")
    stamp = time.strftime("%Y-%m-%d"); out_dir = os.path.join(SC, "results", stamp + "-transcripts")
    if os.path.exists(os.path.join(SC, "results", stamp + ".json")): stamp = time.strftime("%Y-%m-%dT%H%M%S"); out_dir = os.path.join(SC, "results", stamp + "-transcripts")
    os.makedirs(out_dir, exist_ok=True)
    spent, worst, res, stopped = 0.0, CASE_HIGH, {}, False
    for t in selected:
        prompt = open(os.path.join(TASKS, t, "prompt.md"), encoding="utf-8").read()
        for i in range(runs):
            if spent + worst > max_cost: stopped = True; print(f"stop: ${spent:.2f} spent, the next case could cost ${worst:.2f}, over --max-cost ${max_cost:.2f}"); break
            repo, tr = build(t), os.path.join(out_dir, f"{t}-{i + 1}.jsonl")
            cap = min(max_cost - spent, 2.0)
            try:
                p = subprocess.run([claude, "-p", "--output-format", "stream-json", "--verbose", "--max-turns", "30", "--max-budget-usd", f"{cap:.2f}", "--allowedTools", TOOLS],
                                   input=prompt, cwd=repo, capture_output=True, text=True, timeout=900)
                open(tr, "w", encoding="utf-8").write(p.stdout)
                cost = 0.0
                for l in p.stdout.splitlines():
                    try: e = json.loads(l)
                    except ValueError: continue
                    if e.get("type") == "result": cost = float(e.get("total_cost_usd") or e.get("cost_usd") or 0)
                if p.returncode and not cost: print(f"claude failed on {t}: {p.stderr.strip()[-300:]}"); shutil.rmtree(repo, ignore_errors=True); return 2
                rc, score, out = check(t, repo, tr)
            except subprocess.TimeoutExpired:
                cost, rc, score, out = 0.0, 1, 0.0, "timed out after 15 minutes"
            spent += cost; worst = max(worst, cost)
            res.setdefault(t, []).append({"run": i + 1, "score": score, "exit": rc, "cost_usd": round(cost, 4), "transcript": os.path.relpath(tr, ROOT), "check": out})
            print(f"{t} run {i + 1}: score {score:.2f}  cost ${cost:.2f}")
            shutil.rmtree(repo, ignore_errors=True)
        if stopped: break
    done = [t for t in selected if t in res]
    if not done: return 1
    w = max(len(t) for t in done)
    print(f"\n{'task'.ljust(w)}  runs  score  cost")
    avg = {}
    for t in done:
        avg[t] = sum(r["score"] for r in res[t]) / len(res[t])
        print(f"{t.ljust(w)}  {len(res[t]):<4}  {avg[t] * 100:5.1f}  ${sum(r['cost_usd'] for r in res[t]):.2f}")
    total = 100 * sum(avg.values()) / len(avg)
    print(f"\nTOTAL {total:.1f} / 100 over {len(done)} of {len(selected)} tasks, ${spent:.2f} spent" + (" (stopped at the cost cap)" if stopped else ""))
    version = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip() if os.path.exists(os.path.join(ROOT, "VERSION")) else ""
    path = os.path.join(SC, "results", stamp + ".json")
    json.dump({"date": stamp, "adams_version": version, "total": round(total, 1), "tasks_run": len(done), "cost_usd": round(spent, 4), "stopped_at_cap": stopped, "tasks": res}, open(path, "w"), indent=2)
    print("wrote", os.path.relpath(path, ROOT))
    return 0

def main(a):
    if "--dry-run" in a: return dry_run()
    if "--run" in a:
        opt = lambda k, d: a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else d
        sel = [x for x in opt("--tasks", ",".join(names())).split(",") if x]
        bad = [x for x in sel if x not in names()]
        if bad: print("unknown task:", ", ".join(bad), "| known:", ", ".join(names())); return 2
        try: return run(sel, int(opt("--runs", "1")), float(opt("--max-cost", "6")))
        except ValueError: print("--runs needs a whole number and --max-cost a number"); return 2
    print(__doc__); return 0 if not a or "-h" in a or "--help" in a else 2

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
