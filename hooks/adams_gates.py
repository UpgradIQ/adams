"""Shared helpers for the Adams hard gates (align, verify, commit). Imported by the hooks in this folder.
Every gate is off with ADAMS_GATES=0; the verify gate is also off with ADAMS_VERIFY=0. Callers never fail a session on an internal error."""
import fnmatch, hashlib, json, os, re, subprocess, tempfile, time

SRC = (".js", ".jsx", ".ts", ".tsx", ".py", ".go", ".rs", ".rb", ".java", ".php", ".css", ".html", ".sh")
SKIP = {"node_modules", "dist", "build", ".git", ".planning", ".adams"}
# a command that verifies code: test, build, typecheck, lint
VERIFY = re.compile(r"(?:^|[;&|\n(])\s*(?:\w+=\S+\s+)*(?:(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:test|build|typecheck|lint)\b|npx\s+(?:tsc|vitest|jest|eslint)\b"
                    r"|(?:tsc|vitest|jest|pytest|ruff|eslint)\b|python3?\s+-m\s+pytest\b|go\s+(?:test|build|vet)\b|cargo\s+(?:test|build|clippy)\b|make\s+test\b"
                    r"|python3?\s+(?:\S*/)?scripts/(?:selftest|test)\.py\b|adams\s+selftest\b)")
sha1 = lambda b: hashlib.sha1(b).hexdigest()
gates_off = lambda: os.environ.get("ADAMS_GATES") == "0"
verify_off = lambda: gates_off() or os.environ.get("ADAMS_VERIFY") == "0"

def git(cwd, *a):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, errors="replace", timeout=20)
    return r.stdout if r.returncode == 0 else None

def git_top(path):
    """Root of the git work tree holding path (a file or folder, which may not exist yet), or None."""
    d = path
    while d and not os.path.isdir(d) and d != os.path.dirname(d): d = os.path.dirname(d)
    out = git(d, "rev-parse", "--show-toplevel")
    return os.path.realpath(out.strip()) if out and out.strip() else None

def state_path(kind, sid, cwd=""):
    return os.path.join(tempfile.gettempdir(), f"adams-{kind}-" + (re.sub(r"[^\w-]", "_", sid) if sid else sha1(cwd.encode())))

def load(path, default):
    try: return json.load(open(path))
    except Exception: return default

def save(path, data): json.dump(data, open(path, "w"))

def touched(sid):
    """Realpaths this session wrote (recorded by adams_verify_record.py after each edit); an empty set without a session_id or before any edit."""
    return set(load(state_path("touched", sid), [])) if sid else set()

# a shell command that writes files: redirect (not to /dev/null), tee, in-place sed or perl, mv or cp, or a script opening a file for writing
_REDIR = r"(?<![<>\d&=-])>>?\s*[\"']?(?!/dev/null|&)"
_WRITE = r"\btee\b|\b(?:sed|perl)\s+-[\w-]*i|\b(?:mv|cp|patch|truncate|install)\s|\bgit\s+(?:mv|apply)\b|\.write\w*\(|\bopen\([^)]*['\"][wa]|writeFileSync|appendFileSync|\bsponge\b"
BASH_WRITE = re.compile(_REDIR + r"\S|" + _WRITE)
BASH_OTHER, REDIR_TARGET = re.compile(_WRITE), re.compile(_REDIR + r"([^\s;&|<>'\"]+)")

CD = re.compile(r"(?:^|[;&|\n(])\s*(?:cd|pushd)\s+(?:\"([^\"]+)\"|'([^']+)'|([^\s;&|]+))")

def cmd_base(cmd, cwd, upto=None):
    """The folder a command works in: cwd moved by every `cd DIR` or `pushd DIR` that starts before offset upto (all of them when upto is None). Hooks get the session folder as cwd, which
    is not the folder the command runs in after `cd repo && ...`. Shortcut: a `cd` in a subshell or a branch counts like any other; `cd -` and `cd` alone are ignored."""
    for m in CD.finditer(cmd):
        if upto is not None and m.start() >= upto: break
        d = next(x for x in m.groups() if x)
        if d != "-": cwd = os.path.normpath(os.path.join(cwd, os.path.expandvars(os.path.expanduser(d))))
    return cwd

def git_c(text, base):
    """base moved by every `-C DIR` of a git command text (git -C repo commit)."""
    for d in re.findall(r"\s-C\s+[\"']?([^\s\"']+)", text): base = os.path.normpath(os.path.join(base, os.path.expanduser(d)))
    return base

def bash_targets(cmd, cwd, anyext=False):
    """Realpaths of the source files a write-like shell command names, before it runs (the files need not exist yet): redirect targets, plus every path token when the command writes another way
    (tee, sed -i, mv, a script opening a file). A `cd DIR` or `pushd DIR` moves the base (cmd_base). Read-only commands, tests and builds give an empty set; `adams decide` text is never a target.
    Shortcut: any source path token of a non-redirect write counts, even a source file it only reads (cp src/a.js /tmp/x); add per-command parsing when that matters.
    anyext=True returns every path token whatever its extension (the deviation gates classify configs, snapshots and workflows by name)."""
    if not BASH_WRITE.search(cmd) or re.search(r"\badams[\"']?\s+decide\b", cmd): return set()
    base = cmd_base(cmd, cwd)
    toks = REDIR_TARGET.findall(cmd) + (re.findall(r"[\w@%+./~-]+", cmd) if BASH_OTHER.search(cmd) else [])
    return {os.path.realpath(os.path.join(base, os.path.expanduser(t))) for t in toks if anyext or t.lower().endswith(SRC)}

def bash_written(cmd, cwd):
    """Realpaths of changed or new files that a write-like shell command names (a path token, relative to the folder the command works in or the repo root, that git shows as changed).
    A read-only command, or one that names no changed file, gives an empty set. Shortcut: a write-like command that only reads a file another session changed is attributed to this session; add a before/after snapshot if that matters."""
    if not BASH_WRITE.search(cmd): return set()
    base = cmd_base(cmd, cwd)
    top, paths = changed_paths(base)
    if not top: return set()
    changed = {os.path.join(top, p) for p in paths}
    return {q for t in re.findall(r"[\w@%+./~-]+", cmd) for b in (base, top) if (q := os.path.realpath(os.path.join(b, os.path.expanduser(t)))) in changed}

def tree_hash(top):
    """Fingerprint of the working tree: git diff HEAD plus the names and sizes of untracked, non-ignored files (.adams and .planning excluded)."""
    d = git(top, "diff", "HEAD", "--", ".", ":(exclude).adams", ":(exclude).planning")
    if d is None: d = (git(top, "diff", "--cached") or "") + (git(top, "diff") or "")  # no commit yet
    names = sorted(p for p in (git(top, "ls-files", "--others", "--exclude-standard", "-z") or "").split("\0") if p and not p.startswith((".adams/", ".planning/")))
    def size(p):
        try: return os.path.getsize(os.path.join(top, p))
        except OSError: return -1
    return sha1((d + "\0" + "\0".join(f"{p}:{size(p)}" for p in names)).encode("utf-8", "replace"))

def changed_paths(cwd):
    """(repo root, repo-relative paths of changed or untracked files that still exist) from git status."""
    top, out = git_top(cwd), git(cwd, "status", "--porcelain", "-z", "-uall")
    if not top or out is None: return None, []
    paths, parts, i = [], out.split("\0"), 0
    while i < len(parts):
        e = parts[i]; i += 1
        if len(e) < 4: continue
        if e[0] in "RC": i += 1  # rename or copy: the next field is the old path
        if "D" not in e[:2] and os.path.isfile(os.path.join(top, e[3:])): paths.append(e[3:])
    return top, paths

def source_files(paths): return [p for p in paths if p.lower().endswith(SRC) and not SKIP & set(p.split("/"))]

def detect_verify(top):
    """The commands that verify this project, from the files it has. Empty when nothing is detectable."""
    j = lambda *p: os.path.join(top, *p)
    cmds = []
    if os.path.isfile(j("package.json")):
        scripts = (load(j("package.json"), {}) or {}).get("scripts") or {}
        run = "pnpm" if os.path.exists(j("pnpm-lock.yaml")) else "yarn" if os.path.exists(j("yarn.lock")) else "bun" if os.path.exists(j("bun.lockb")) or os.path.exists(j("bun.lock")) else "npm"
        cmds += [f"{run} test" if n == "test" else f"{run} run {n}" for n in ("test", "build", "typecheck", "lint") if n in scripts]
    if os.path.isfile(j("go.mod")): cmds.append("go test ./...")
    if os.path.isfile(j("Cargo.toml")): cmds.append("cargo test")
    cfg = lambda f: os.path.isfile(j(f)) and "pytest" in open(j(f), encoding="utf-8", errors="ignore").read()
    if cfg("pyproject.toml") or cfg("setup.cfg") or cfg("tox.ini") or os.path.isfile(j("pytest.ini")) or (os.path.isdir(j("tests")) and any(f.endswith(".py") for f in os.listdir(j("tests")))): cmds.append("pytest")
    cmds += [f"python3 scripts/{n}.py" for n in ("selftest", "test") if os.path.isfile(j("scripts", n + ".py"))]
    return cmds

def needs_verify(top, sid, cwd=""):
    """The commands to run when the tree differs from the latest green verification of this session; [] when verified, opted out or nothing is detectable."""
    if verify_off(): return []
    cmds = detect_verify(top)
    if not cmds: return []
    ok = [r for r in load(state_path("verify", sid, cwd), []) if r.get("ok") and r.get("top") == top]
    return [] if ok and ok[-1].get("tree_hash") == tree_hash(top) else cmds

def mask(v): return "[****" + v[-4:] + "]"

# --- agent deviation gates: shared pieces (hooks/adams_deviation_gate.py, block-risky-git.py, adams_stop.py, adams_router.py)
TESTY = re.compile(r"(?:^|/)(?:tests?|__tests__|specs?|e2e)/|(?:^|/)test_[^/]*$|[._-](?:tests?|spec)\.\w+$|\.(?:test|spec)\.", re.I)
ASKED = re.compile(r"\b(?:ci|workflows?|thresholds?|snapshots?|selftest)\b", re.I)  # the user's words that let the agent touch a referee (CI, thresholds, snapshots)
LOG = r"- (\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d): (.*)"  # a bullet of .adams/decisions.md written by `adams decide`

def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))

def is_adams_repo(top):
    """True for a work tree of the Adams source itself (not the installed plugin copy), where editing its own hooks and scripts is allowed."""
    plugins = os.path.realpath(os.path.expanduser("~/.claude/plugins")) + os.sep
    return bool(top) and os.path.isfile(os.path.join(top, "hooks", "adams_gates.py")) and not os.path.realpath(top).startswith(plugins)

def session_t0(sid, cwd="", create=True):
    """Time of this session's first deviation-gate call (state adams-session-<id>); None when never recorded and create is False."""
    sp = state_path("session", sid, cwd); st = load(sp, {})
    if "t0" not in st and create: st["t0"] = time.time(); save(sp, st)
    return st.get("t0")

def decisions_since(top, t0):
    """Texts of the .adams/decisions.md bullets recorded at or after t0 (bullets without a time, written by older versions, never count)."""
    try: lines = open(os.path.join(top, ".adams", "decisions.md"), encoding="utf-8").read().splitlines()
    except OSError: return []
    out = []
    for l in lines:
        m = re.fullmatch(LOG, l)
        if m and time.mktime(time.strptime(m[1] + " " + m[2], "%Y-%m-%d %H:%M:%S")) >= int(t0 or 0): out.append(m[3])
    return out

def scope_globs(top, sid, cwd=""):
    """The globs of the latest `adams decide --scope` recorded this session (repo relative); [] means no scope, so nothing is enforced."""
    notes = [n for n in decisions_since(top, session_t0(sid, cwd)) if n.startswith("scope: ")]
    return [x.strip() for x in notes[-1][7:].split(",") if x.strip()] if notes else []

def scope_ok(rel, globs):
    """True when rel is inside the scope, or is a test, a doc, .adams or .planning (always allowed)."""
    if TESTY.search(rel) or rel.lower().endswith((".md", ".txt")) or rel.startswith(("docs/", ".adams/", ".planning/")): return True
    return any(rel == x or (x.endswith("/") and rel.startswith(x)) or fnmatch.fnmatchcase(rel, x) or (x.startswith("**/") and fnmatch.fnmatchcase(rel, x[3:])) for x in globs)
