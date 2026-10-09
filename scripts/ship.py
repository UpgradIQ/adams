#!/usr/bin/env python3
"""Fast agent execution and review loop: wait for the checks, merge, mark the task, hand over the next prompt (stdlib plus the gh CLI).
  ship.py ship PR [TASK_ID [NEXT_ID]] [--go] [--yes] [--wait MIN]   wait for the fast checks, merge, mark TASK_ID done, copy NEXT_ID's prompt
  ship.py ship --set key=value        save one setting in .adams/ship.json (the first `ship` asks for auto_merge)
  ship.py next                        every todo task whose dependencies are done, one `ID  title` per line
  ship.py watch                       your open PRs (not on the base branch): task, size, risk tier
  ship.py all [--session ID] [--mine FILE,..] [--leave] [--yes] [--message TEXT]
                                      commit your files by name, push, open the PR, merge every open PR of yours: two lines, Shipped and Left
Exit codes: 0 done (MERGED, QUEUED, READY, a listing) | 1 not merged (a check failed, wrong base, merge refused) or items left | 2 gh missing or not signed in, bad
settings or usage | 3 ASK auto_merge | 4 ASK high-risk | 5 ASK files | 6 checks still running at the time cap.
Settings (all optional) in .adams/ship.json: base, auto_merge (yes|no), skip_checks [names or globs], tracker, prompts_file, deps_field, risk {high:[globs], low:[globs]},
max_wait_minutes. Never bypasses branch protection: no --admin, no force push, no branch switch in the main checkout. Details: docs/OPERATIONS.md."""
import argparse, fnmatch, json, os, re, shlex, shutil, subprocess, sys, time
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import track  # noqa: E402

DELAYS = (10, 20, 40, 60)  # seconds between check polls, then 60 until the cap
HIDDEN = (".adams/", ".planning/")  # workflow state, never committed or asked about by `all`
OUT = sys.stdout  # `all` moves progress to stderr so its stdout is exactly two lines


class Stop(Exception):
    """End the run with one line and an exit code."""
    def __init__(self, line, code=2): super().__init__(line); self.line, self.code = line, code


class Gh(Exception): pass


def say(msg): print(msg, file=OUT)


def first(r):
    t = (r.stderr or r.stdout or "").strip()
    return t.splitlines()[0] if t else f"exit {r.returncode}"


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def git(*a, cwd=None): return run(["git", *a], cwd)


AUTH = re.compile(r"gh auth login|not logged in|authentication|GH_TOKEN|HTTP 401", re.I)


def need_gh():
    if not shutil.which("gh"): raise Stop("gh is not installed: get the GitHub CLI from https://cli.github.com, then run: gh auth login")


def gh(*a, soft=False):
    """Run gh. A missing or signed-out gh ends the run with one line; a failing call raises Gh unless soft (then the caller reads returncode)."""
    need_gh()
    r = run(["gh", *a])
    if r.returncode == 0 or (soft and not AUTH.search(r.stderr or "")): return r
    if AUTH.search(r.stderr or r.stdout or ""): raise Stop("gh is not signed in: run gh auth login")
    raise Gh(first(r))


def gj(*a):
    try: return json.loads(gh(*a).stdout or "null")
    except ValueError: raise Gh(f"gh {a[0]} {a[1]} returned no JSON")


# ---- settings -------------------------------------------------------------------------------------------------------------------------------
def _risk_ok(v):
    return isinstance(v, dict) and all(k in ("high", "low") and isinstance(x, list) and all(isinstance(g, str) for g in x) for k, x in v.items())


SCHEMA = {"base": (lambda v: isinstance(v, str) and v, "a branch name"), "auto_merge": (lambda v: v in ("yes", "no"), "yes or no"),
          "skip_checks": (lambda v: isinstance(v, list) and all(isinstance(x, str) for x in v), "a list of check names or globs"),
          "tracker": (lambda v: isinstance(v, str) and v, "a file path"), "prompts_file": (lambda v: isinstance(v, str) and v, "a file path"),
          "deps_field": (lambda v: isinstance(v, str) and v, "a task field name"), "risk": (_risk_ok, "an object with high and low lists of globs"),
          "max_wait_minutes": (lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0, "a number of minutes above 0")}


def validate(d, where, strict=False):
    if not isinstance(d, dict): raise Stop(f"{where}: must be a JSON object")
    for k, v in d.items():
        if k not in SCHEMA:
            if strict: raise Stop(f"unknown setting '{k}' (known: {', '.join(SCHEMA)})")
            print(f"ship: ignoring unknown setting '{k}' in {where}", file=sys.stderr); continue
        if not SCHEMA[k][0](v): raise Stop(f"{where}: '{k}' must be {SCHEMA[k][1]}")
    return {k: v for k, v in d.items() if k in SCHEMA}


class Ctx:
    """Where we are: the checkout, the main checkout, the settings, the tracker."""
    def __init__(self):
        self.cwd = os.getcwd()
        t = git("rev-parse", "--show-toplevel", cwd=self.cwd)
        self.top = os.path.realpath(t.stdout.strip()) if t.returncode == 0 and t.stdout.strip() else self.cwd
        self.main = self.top
        c = git("rev-parse", "--git-common-dir", cwd=self.top)
        if c.returncode == 0 and c.stdout.strip():
            p = os.path.realpath(os.path.join(self.top, c.stdout.strip()))
            if os.path.basename(p) == ".git": self.main = os.path.dirname(p)
        self.roots = [self.top] + ([self.main] if self.main != self.top else [])
        self.sfile = next((p for r in self.roots for p in [os.path.join(r, ".adams", "ship.json")] if os.path.isfile(p)), None)
        self.s = {}
        if self.sfile:
            try: self.s = validate(json.load(open(self.sfile, encoding="utf-8")), os.path.relpath(self.sfile, self.cwd))
            except ValueError: raise Stop(f"{self.sfile} is not valid JSON")
        rel = self.s.get("tracker", ".planning/track.md")
        self.tracker = next((p for r in self.roots for p in [os.path.join(r, rel)] if os.path.isfile(p)), None)
        self._base = self.s.get("base")

    @property
    def base(self):
        if not self._base: self._base = (gj("repo", "view", "--json", "defaultBranchRef").get("defaultBranchRef") or {}).get("name") or "main"
        return self._base

    def branch(self): return git("rev-parse", "--abbrev-ref", "HEAD", cwd=self.top).stdout.strip()


def save_setting(c, kv):
    k, _, raw = kv.partition("=")
    if not k or not _: raise Stop("usage: ship --set key=value")
    try: v = json.loads(raw)
    except ValueError: v = raw
    if k == "auto_merge" and isinstance(v, bool): v = "yes" if v else "no"
    validate({k: v}, "--set", strict=True)
    path = c.sfile or os.path.join(c.main, ".adams", "ship.json")
    cur = json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else {}
    cur[k] = v
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(json.dumps(cur, indent=2) + "\n")
    say(f"saved {k}={json.dumps(v)} in {path}")


# ---- risk tiers -----------------------------------------------------------------------------------------------------------------------------
TOKEN = lambda *w: r"(?:^|[/._-])(?:" + "|".join(w) + r")(?:[/._-]|$)"
HIGH = [r"(?:^|/)migrations?/", r"\.sql$", TOKEN("auth", "oauth", "permissions?", "polic(?:y|ies)", "rls"), TOKEN("payments?", "billing", "stripe"), r"(?:^|/)\.env(?:\.|$)",
        TOKEN("secrets?"), r"(?:^|/)\.github/workflows/", r"(?:^|/)(?:\.gitlab-ci\.ya?ml|\.circleci/|azure-pipelines|jenkinsfile|\.travis\.yml|bitbucket-pipelines|\.buildkite/)",
        TOKEN("delet(?:e|ion)", "drop", "purge")]
LOW = [r"(?:^|/)docs?/", r"\.mdx?$", r"(?:^|/)generated/", r"\.lock$", r"(?:^|/)(?:package-lock\.json|pnpm-lock\.yaml)$", r"(?:^|/)dist/"]


def patterns(globs, defaults):
    if globs is None: return [re.compile(p, re.I) for p in defaults]
    return [re.compile(r"\A" + fnmatch.translate(x)) for g in globs for x in (g, "*/" + g)]


def risk_tier(files, risk=None):
    """high, low or normal from the changed paths. high wins; low needs every path low. A settings `risk` list replaces that tier's defaults."""
    risk = risk or {}
    hi, lo = patterns(risk.get("high"), HIGH), patterns(risk.get("low"), LOW)
    hits = [f for f in files if any(p.search(f) for p in hi)]
    if hits: return "high", hits
    if files and all(any(p.search(f) for p in lo) for f in files): return "low", []
    return "normal", []


def names(files, n=5): return ", ".join(files[:n]) + (f" and {len(files) - n} more" if len(files) > n else "")


def task_id(*texts):
    for t in texts:
        m = re.search(r"[A-Za-z]+-\d+", t or "")
        if m: return m.group(0)
    return None


# ---- the ship steps -------------------------------------------------------------------------------------------------------------------------
def bucket(ck):
    b = (ck.get("bucket") or "").lower()
    if b: return b
    s = (ck.get("state") or "").upper()
    return "pass" if s in ("SUCCESS", "NEUTRAL") else "skipping" if s == "SKIPPED" else "pending" if s in ("PENDING", "IN_PROGRESS", "QUEUED", "WAITING", "REQUESTED") else "fail"


def poll_checks(pr, skip, cap_min):
    """Wait for the fast checks with one `gh pr checks` call per poll. Returns ('ok'|'failed'|'running', names, note)."""
    waited, i, empty, cap = 0, 0, 0, cap_min * 60
    scale = float(os.environ.get("ADAMS_SHIP_POLL_SCALE", "1"))
    while True:
        r = gh("pr", "checks", pr, "--json", "name,state,bucket", soft=True)  # gh exits non-zero for pending or failed checks and still prints the JSON
        out = (r.stdout or "").strip()
        try: allc = json.loads(out) if out else [] if r.returncode == 0 or re.search(r"no checks reported", r.stderr or "", re.I) else None
        except ValueError: allc = None
        if allc is None: raise Gh(first(r))
        fast = [c for c in allc if not any(fnmatch.fnmatchcase(c.get("name", ""), g) for g in skip)]
        failed = [c["name"] for c in fast if bucket(c) in ("fail", "cancel")]
        if failed: return "failed", failed, ""
        pending = [c["name"] for c in fast if bucket(c) == "pending"]
        if allc and not pending: return "ok", [], ""
        if not allc:
            empty += 1
            if empty > 3: return "ok", [], "no checks reported after 70 seconds, merging without CI"
        if waited >= cap: return "running", pending, ""
        d = DELAYS[min(i, len(DELAYS) - 1)]; i += 1; waited += d
        time.sleep(d * scale)


def copy(text):
    for cmd in (["pbcopy"], ["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"], ["clip.exe"], ["clip"]):
        if shutil.which(cmd[0]):
            try:  # stdout and stderr go to the null device: wl-copy and xclip stay alive holding the pipe
                if subprocess.run(cmd, input=text, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10).returncode == 0: return True
            except (OSError, subprocess.SubprocessError): pass
    return False


def prompt_for(c, nid):
    """The prompt of task nid: prompts_file (JSON list of {id, prompt} or object id -> prompt), else the tracker task's `agent prompt`."""
    pf = c.s.get("prompts_file")
    p = next((q for r in c.roots for q in [os.path.join(r, pf)] if os.path.isfile(q)), None) if pf else None
    if p:
        try: data = json.load(open(p, encoding="utf-8"))
        except ValueError: return None
        if isinstance(data, list): data = {str(x.get("id")): x.get("prompt") for x in data if isinstance(x, dict)}
        hit = next((v for k, v in (data.items() if isinstance(data, dict) else []) if k.upper() == nid.upper()), None)
        if isinstance(hit, str): return hit
    if c.tracker:
        d, _ = track.parse(open(c.tracker, encoding="utf-8").read())
        t = next((t for t in d["tasks"] if t["id"].upper() == nid.upper()), None)
        if t: return t["f"].get("agent prompt")
    return None


def mark_done(c, tid, n, sha, quiet):
    """Set tid done in the tracker. Returns the text for the MERGED line, or None."""
    if not c.tracker: return None if quiet else f"no tracker, {tid} not marked"
    d, _ = track.parse(open(c.tracker, encoding="utf-8").read())
    tid = next((t["id"] for t in d["tasks"] if t["id"].upper() == tid.upper()), None) or tid
    if tid not in [t["id"] for t in d["tasks"]]: return None if quiet else f"{tid} not in the tracker"
    try: track.set_file(c.tracker, tid, "done", f"PR #{n} merged as {sha} ({date.today().isoformat()})")
    except (OSError, ValueError) as e: return f"tracker not updated ({e})"
    return f"{tid} done"


def finish(c, n, sha, tid, nxt, quiet):
    parts = [f"MERGED #{n} {sha}"]
    if tid:
        m = mark_done(c, tid, n, sha, quiet)
        if m: parts.append(m)
    extra = None
    if nxt:
        p = prompt_for(c, nxt)
        if not p: parts.append(f"{nxt} prompt not found")
        elif copy(p): parts.append(f"{nxt} copied")
        else: parts.append(f"{nxt} prompt below"); extra = p
    say("; ".join(parts))
    if extra: say(extra)
    return "merged", f"#{n} {tid + ' ' if tid else ''}{sha}"


def ship_pr(c, pr, tid=None, nxt=None, go=False, yes=False, wait=None, quiet=False):
    """Wait, merge, mark. Returns (kind, text): merged | queued | ready | failed | refused | running | high. The first line of output says tier and size."""
    v = gj("pr", "view", pr, "--json", "number,state,isDraft,baseRefName,additions,deletions,changedFiles")
    n = v["number"]; tag = f"#{n}"
    if v["state"] == "MERGED":
        sha = ((gj("pr", "view", pr, "--json", "mergeCommit").get("mergeCommit") or {}).get("oid") or "")[:8]
        return finish(c, n, sha, tid, nxt, quiet)
    if v["state"] != "OPEN": return "failed", f"{tag} is {v['state'].lower()}"
    if v["baseRefName"] != c.base:
        say(f"NOT MERGED {tag}: targets {v['baseRefName']}, not the base branch {c.base}")
        return "refused", f"{tag} targets {v['baseRefName']}, not {c.base}"
    if v.get("isDraft"):
        say(f"NOT MERGED {tag}: the PR is a draft")
        return "refused", f"{tag} is a draft"
    files = [x.strip() for x in gh("pr", "diff", pr, "--name-only").stdout.splitlines() if x.strip()]
    tier, hits = risk_tier(files, c.s.get("risk"))
    say(f"{tag} {tier} risk, {v['changedFiles']} files, +{v['additions']} -{v['deletions']}")
    if tier == "high" and not yes:
        say(f"ASK high-risk {tag}: touches {names(hits)}; merge? (rerun with --yes)")
        return "high", f"{tag} high risk, touches {names(hits, 3)}"
    status, bad, note = poll_checks(pr, c.s.get("skip_checks", []), wait or c.s.get("max_wait_minutes", 45))
    if status == "failed":
        say(f"NOT MERGED {tag}: failed {', '.join(bad)}")
        return "failed", f"{tag} failed {', '.join(bad)}"
    if status == "running":
        say(f"STILL RUNNING {tag}: {', '.join(bad)} not finished, rerun later")
        return "running", f"{tag} checks still running ({', '.join(bad)})"
    if note: say(note)
    if not (go or c.s.get("auto_merge") == "yes"):
        say(f"READY {tag}: checks green, say go to merge")
        return "ready", f"{tag} waiting for go"
    queued = False
    if gj("repo", "view", "--json", "autoMergeAllowed").get("autoMergeAllowed"):
        queued = gh("pr", "merge", pr, "--auto", "--squash", soft=True).returncode == 0
    if not queued:
        r = gh("pr", "merge", pr, "--squash", soft=True)
        if r.returncode != 0:
            say(f"NOT MERGED {tag}: {first(r)}")
            return "failed", f"{tag} merge refused: {first(r)}"
    st = gj("pr", "view", pr, "--json", "state,mergeCommit")
    if st.get("state") != "MERGED":
        say(f"QUEUED {tag}: GitHub merges it when the required checks pass; rerun to mark the task")
        return "queued", f"{tag} queued"
    return finish(c, n, ((st.get("mergeCommit") or {}).get("oid") or "")[:8], tid, nxt, quiet)


def pull_base(c):
    """git pull --ff-only in the main checkout, only when it sits on the base branch with no tracked changes. Returns a note when it did not pull."""
    br = git("rev-parse", "--abbrev-ref", "HEAD", cwd=c.main).stdout.strip()
    if br != c.base: return f"main checkout is on {br}, not {c.base}: not pulled"
    dirty = [l for l in git("status", "--porcelain", "--untracked-files=no", cwd=c.main).stdout.splitlines() if not l[3:].startswith(HIDDEN)]
    if dirty: return f"main checkout has uncommitted changes: not pulled"
    r = git("pull", "--ff-only", cwd=c.main)
    return None if r.returncode == 0 else f"git pull --ff-only failed: {first(r)}"


# ---- commands -------------------------------------------------------------------------------------------------------------------------------
def cmd_ship(argv):
    ap = argparse.ArgumentParser(prog="ship ship")
    ap.add_argument("pr", nargs="?"); ap.add_argument("task", nargs="?"); ap.add_argument("next", nargs="?")
    ap.add_argument("--go", action="store_true"); ap.add_argument("--yes", action="store_true"); ap.add_argument("--wait", type=float); ap.add_argument("--set")
    a = ap.parse_args(argv)
    c = Ctx()
    if a.set: save_setting(c, a.set); return 0
    if not a.pr: ap.error("PR is required")
    need_gh()
    if "auto_merge" not in c.s:
        say("ASK auto_merge: Merge automatically when the fast checks pass? (answer with: adams ship --set auto_merge=yes|no)")
        return 3
    kind, _ = ship_pr(c, a.pr, a.task, a.next, a.go, a.yes, a.wait)
    if kind == "merged":
        note = pull_base(c)
        if note: say(note)
    return {"merged": 0, "queued": 0, "ready": 0, "high": 4, "running": 6}.get(kind, 1)


def cmd_next(argv):
    c = Ctx()
    if not c.tracker: raise Stop(f"no tracker found at {c.s.get('tracker', '.planning/track.md')}")
    d, _ = track.parse(open(c.tracker, encoding="utf-8").read())
    rows = track.ready(d, c.s.get("deps_field", "depends"))
    for t in rows: say(f"{t['id']}  {t['f'].get('title') or t['name']}")
    if not rows: print("no todo task is unblocked", file=sys.stderr)
    return 0


def cmd_watch(argv):
    c = Ctx()
    me = gj("api", "user").get("login")
    prs = gj("pr", "list", "--state", "open", "--limit", "100", "--json", "number,title,headRefName,author,additions,deletions,changedFiles,files") or []
    mine = [p for p in prs if (p.get("author") or {}).get("login") == me and p["headRefName"] != c.base]
    for p in sorted(mine, key=lambda p: p["number"]):
        # shortcut: gh returns at most 100 files per PR here, so a very large PR may read a lower tier than `ship` finds
        tier, _ = risk_tier([f["path"] for f in p.get("files") or []], c.s.get("risk"))
        say(f"#{p['number']}  {task_id(p['headRefName'], p['title']) or '-':<8} {tier:<6} {p['changedFiles']} files +{p['additions']} -{p['deletions']}  {p['title']}")
    if not mine: print("no open PR of yours outside the base branch", file=sys.stderr)
    return 0


def status_entries(top):
    """(XY, path, old path or None) for every changed or untracked file outside .adams and .planning."""
    out, res, i = git("status", "--porcelain", "-z", "-uall", cwd=top).stdout.split("\0"), [], 0
    while i < len(out):
        e = out[i]; i += 1
        if len(e) < 4: continue
        old = None
        if e[0] in "RC": old = out[i]; i += 1  # the old path of a rename or copy follows
        if not e[3:].startswith(HIDDEN): res.append((e[:2], e[3:], old))
    return res


def own_files(top, sid):
    """Realpaths this session wrote and still holds, from the Stop hook's touched state (hooks/adams_gates.py mine()); empty when unknown."""
    if not sid: return set()
    try:
        sys.path.insert(0, os.path.join(HERE, "..", "hooks"))
        import adams_gates as ag
        return ag.mine(sid)
    except Exception: return set()


def commit_message(entries, top):
    paths = [p for _, p, _o in entries]
    nm = [os.path.basename(p) for p in paths]
    docs = all(p.lower().endswith((".md", ".mdx", ".txt")) or p.startswith("docs/") for p in paths)
    tests = all(re.search(r"(?:^|/)(?:tests?|__tests__|specs?)/|[._-](?:tests?|spec)\.", p, re.I) for p in paths)
    verb = "add" if all(x in ("??", "A ") for x, _, _o in entries) else "delete" if all("D" in x for x, _, _o in entries) else "update"
    ns = git("diff", "--numstat", "HEAD", "--", *paths, cwd=top).stdout.split()
    add = sum(int(x) for x in ns[0::3] if x.isdigit()); dele = sum(int(x) for x in ns[1::3] if x.isdigit())
    msg = f"{'docs' if docs else 'test' if tests else 'chore'}: {verb} {', '.join(nm[:2])}" + (f" and {len(nm) - 2} more" if len(nm) > 2 else "") + (f" (+{add} -{dele})" if add or dele else "")
    return msg if len(msg) <= 100 else msg[:97] + "..."


def commit_gate(c, cmd, sid):
    """The reasons the Adams commit gate (hooks/block-risky-git.py) would give for this commit; [] when it passes or the gate is unavailable."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("brg", os.path.join(HERE, "..", "hooks", "block-risky-git.py"))
        g = importlib.util.module_from_spec(spec); sys.path.insert(0, os.path.join(HERE, "..", "hooks")); spec.loader.exec_module(g)
        return g.commit_gate(cmd, c.top, sid)
    except Exception: return []


def cmd_all(argv):
    global OUT
    OUT = sys.stderr
    ap = argparse.ArgumentParser(prog="ship all")
    ap.add_argument("--session", default=os.environ.get("CLAUDE_SESSION_ID", "")); ap.add_argument("--mine", nargs="+", default=[])
    ap.add_argument("--leave", action="store_true"); ap.add_argument("--yes", action="store_true"); ap.add_argument("--message"); ap.add_argument("--wait", type=float)
    a = ap.parse_args(argv)
    if a.session.startswith("${"): a.session = ""  # a slash command placeholder that was not substituted
    c = Ctx()
    need_gh()
    br = c.branch()
    if br in (c.base, "HEAD"):
        raise Stop(f"NOT SHIPPED: on {'a detached HEAD' if br == 'HEAD' else 'the base branch ' + c.base}; start from a branch or worktree "
                   f"(git worktree add ../work -b feat/name origin/{c.base}) and run it there", 1)
    shipped, left = [], []
    # 1. commit this session's files by name; foreign files are only listed
    entries = status_entries(c.top)
    own = own_files(c.top, a.session)
    said = {os.path.normpath(x) for m in a.mine for x in m.split(",") if x}
    mine = [e for e in entries if os.path.realpath(os.path.join(c.top, e[1])) in own or os.path.normpath(e[1]) in said]
    other = [e[1] for e in entries if e not in mine]
    if other and not (a.mine or a.leave):
        print(f"ASK files: not known to be this session's: {names(other, 8)}; commit them (rerun with --mine {','.join(other[:8])}) or leave them (rerun with --leave)")
        return 5
    if mine:
        paths = [q for _, p, o in mine for q in (p, o) if q]
        msg = a.message or commit_message(mine, c.top)
        q = " ".join(shlex.quote(p) for p in paths)
        why = commit_gate(c, f"git add -- {q} && git commit -m {shlex.quote(msg)} -- {q}", a.session)
        if why: left.append("commit blocked by the commit gate: " + "; ".join(why))
        else:
            r = git("add", "--", *paths, cwd=c.top)
            r = git("commit", "-m", msg, "--", *paths, cwd=c.top) if r.returncode == 0 else r
            if r.returncode != 0: left.append(f"commit failed: {first(r)}")
            else: shipped.append(f"committed {len(paths)} file{'s' if len(paths) != 1 else ''}")
    if other: left.append(f"{len(other)} file{'s' if len(other) != 1 else ''} not yours ({names(other, 4)})")
    # 2. push (never forced) and open the PR when the branch has none
    r = git("push", "-u", "origin", "HEAD", cwd=c.top)
    if r.returncode != 0: left.append(f"push failed: {first(r)}")
    else:
        v = gh("pr", "view", "--json", "number,state", soft=True)
        cur = json.loads(v.stdout or "{}") if v.returncode == 0 else {}
        if cur.get("state") != "OPEN":
            r = gh("pr", "create", "--fill", "--base", c.base, soft=True)
            m = re.search(r"/pull/(\d+)", r.stdout or "")
            if r.returncode != 0 or not m: left.append(f"no PR opened: {first(r)}")
    # 3. every open PR of mine off the base branch, in task-id order
    me = gj("api", "user").get("login")
    prs = [p for p in gj("pr", "list", "--state", "open", "--limit", "100", "--json", "number,title,headRefName,author") or []
           if (p.get("author") or {}).get("login") == me and p["headRefName"] != c.base]
    key = lambda p: (lambda t: (t.split("-")[0].upper(), int(t.split("-")[1])) if t else ("~", p["number"]))(task_id(p["headRefName"], p["title"]))
    merged_any, high = False, False
    for p in sorted(prs, key=key):
        tid = task_id(p["headRefName"], p["title"])
        try: kind, text = ship_pr(c, str(p["number"]), tid, None, True, a.yes, a.wait, quiet=True)
        except Gh as e: kind, text = "failed", f"#{p['number']} {e}"
        if kind in ("merged", "queued"): shipped.append(text); merged_any = merged_any or kind == "merged"
        else: left.append(text); high = high or kind == "high"
    # 4. bring the base branch up to date in the main checkout
    if merged_any:
        note = pull_base(c)
        if note: left.append(note)
    OUT = sys.stdout
    print("Shipped: " + ("; ".join(shipped) or "nothing"))
    print("Left: " + ("; ".join(left) or "none"))
    return 4 if high else 1 if left else 0


CMDS = {"ship": cmd_ship, "next": cmd_next, "watch": cmd_watch, "all": cmd_all}


def main(argv):
    if not argv or argv[0] not in CMDS: print(__doc__); return 2
    try: return CMDS[argv[0]](argv[1:])
    except Stop as e: print(e.line); return e.code
    except Gh as e: print(f"gh failed: {e}"); return 2


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
