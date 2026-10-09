#!/usr/bin/env python3
"""PreToolUse hook (Bash): blocks the git commands that break the team's rules or cannot be undone.
Reads the hook JSON on stdin; exit 2 with a message on stderr blocks the command, exit 0 allows it.
Normal `git push` stays allowed. A person can still run a blocked command themselves (the ! prefix in Claude Code).
Also blocks the other destructive commands: git commit --no-verify, a force push (even --force-with-lease) to main or master, rm -r on the repo root or a tracked folder, SQL DROP and TRUNCATE
through a database client, supabase db reset, prisma migrate reset.
Also the commit gate: `git commit` is denied for a secret in what is staged, a `fix` or a feature (feat, add, implement) without a test, source changed since the last green verification,
once per session for a review of the staged source before the first commit, staged files outside the scope recorded with `adams decide --scope`,
and leftovers in the added lines of source (console.log, debugger, print debugging, new TODO or FIXME, mock data in production paths).
ADAMS_GATES=0 turns the commit gate and the extra shell checks off (the git checks stay on), ADAMS_VERIFY=0 only the verification part, ADAMS_REVIEW=0 only the review part."""
import base64, json, os, re, shlex, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adams_gates as ag

def segments(cmd):
    return [s for s in re.split(r"&&|\|\||;|\n|\|", cmd) if s.strip()]

def git_args(seg):
    try: t = shlex.split(seg, posix=True)
    except ValueError: return None
    while t and re.fullmatch(r"[A-Za-z_]\w*=.*", t[0]): t = t[1:]  # leading VAR=value
    if not t or t[0] != "git": return None
    t = t[1:]
    while t and t[0].startswith("-"):  # global options: -C path, -c k=v, --git-dir=...
        t = t[2:] if t[0] in ("-C", "-c") else t[1:]
    return t

def verdict(t):
    if not t: return None
    sub, a = t[0], t[1:]
    flags = [x for x in a if x.startswith("-")]
    short = lambda ch: any(re.fullmatch(r"-[A-Za-z]+", f) and ch in f[1:] for f in flags)
    if sub == "add" and ("--all" in a or "-u" in a or "--update" in a or short("A") or "." in a or ":/" in a):
        return "git add -A / . / -u sweeps in files other sessions changed. Name the files you changed: git add path1 path2"
    if sub == "commit" and ("--all" in a or short("a")):
        return "git commit -a commits every tracked change. Stage the files you changed by name, then commit"
    if sub == "reset" and "--hard" in a: return "git reset --hard deletes uncommitted work and cannot be undone"
    if sub == "clean" and (short("f") or "--force" in a) and not short("n") and "--dry-run" not in a:
        return "git clean -f deletes untracked files for good"
    if sub in ("checkout", "restore") and ("." in a or ":/" in a): return f"git {sub} . throws away every uncommitted change"
    if sub == "branch" and ("-D" in a or ("--delete" in a and "--force" in a) or short("D")): return "git branch -D deletes a branch even if unmerged"
    if sub == "push" and ("--force" in a or "-f" in a or any(x.startswith("+") and len(x) > 1 for x in a)):
        return "force push rewrites remote history (--force-with-lease is allowed)"
    if sub == "push" and any(x.startswith("--force-with-lease") or x == "--force-if-includes" for x in a) and any(re.search(r"(?:^|[:+])(?:main|master)$", x) for x in a):
        return "force push to main or master rewrites shared history"
    if sub in ("commit", "push") and ("--no-verify" in a or (sub == "commit" and short("n"))): return f"git {sub} --no-verify skips the hooks that guard the repo. Fix what the hook reports instead"
    return None

SQL_CLIENT = re.compile(r"(?:psql|mysql|mariadb|sqlite3?|sqlcmd|supabase|prisma|duckdb|clickhouse-client|mongosh|pg_\w+)", re.I)  # a command word, so grep or cat on a migration is not a client
WRAPPERS = {"sudo", "npx", "bunx", "env", "time", "pnpm", "yarn", "dlx", "exec"}
SQL_DESTRUCTIVE = re.compile(r"\bDROP\s+(?:TABLE|DATABASE|SCHEMA)\b|\bTRUNCATE\b", re.I)
RESET = re.compile(r"\bsupabase\s+db\s+reset\b|\bprisma\s+migrate\s+reset\b")
RM_OK = {"node_modules", "dist", "build", ".next", "coverage", "tmp", "scratch"}  # folders that are rebuilt, so removing them is fine

def rm_verdict(cmd, cwd):
    """rm -r on the repo root, the home folder, / or a tracked folder (rebuilt folders such as node_modules, dist and coverage are fine)."""
    base = ag.cmd_base(cmd, cwd)
    for seg in segments(cmd):
        try: t = shlex.split(seg)
        except ValueError: t = seg.split()
        while t and re.fullmatch(r"[A-Za-z_]\w*=.*", t[0]): t = t[1:]
        if not t or t[0] != "rm" or not any(re.fullmatch(r"-[A-Za-z]*[rR][A-Za-z]*", x) or x == "--recursive" for x in t[1:]): continue
        for a in (x for x in t[1:] if not x.startswith("-")):
            p = os.path.realpath(os.path.join(base, os.path.expanduser(a)))
            top = ag.git_top(p)
            if p in ("/", os.path.realpath(os.path.expanduser("~"))) or (top and (p == top or (a.rstrip("/").endswith("*") and os.path.dirname(p) == top))): return f"rm -r on {a} would delete the repo root, your home folder or the whole disk"
            if top and os.path.isdir(p) and p.startswith(top + os.sep) and os.path.basename(p) not in RM_OK and ag.git(top, "ls-files", "--", os.path.relpath(p, top)): return f"rm -r on {a} deletes a tracked folder. Delete the files you mean by name, or ask the user"
    return None

def first_word(seg):
    try: t = shlex.split(seg)
    except ValueError: t = seg.split()
    t = [x for x in t if not re.fullmatch(r"[A-Za-z_]\w*=.*", x)]
    while t and t[0] in WRAPPERS: t = t[1:]
    return t[0] if t else ""

def shell_check(cmd, cwd):
    """Verdict for the non-git destructive commands: rm -r, SQL drops through a database client, database resets."""
    if RESET.search(cmd): return "a database reset deletes all data. Ask the user to run it themselves"
    if SQL_DESTRUCTIVE.search(cmd) and any(SQL_CLIENT.fullmatch(os.path.basename(w)) for w in map(first_word, segments(cmd))): return "DROP and TRUNCATE delete data for good. Ask the user to run it themselves"
    return rm_verdict(cmd, cwd) if re.search(r"\brm\b", cmd) else None

def check(cmd, cwd=None):
    for seg in segments(cmd):
        v = verdict(git_args(seg))
        if v: return v
    return shell_check(cmd, cwd) if cwd else None

COMMIT = re.compile(r"(?:^|[;&|\n(])\s*(?:\w+=\S+\s+)*git(?:\s+(?:-C\s+\S+|-c\s+\S+|--[\w-]+))*\s+commit\b")
ADD = re.compile(r"(?:^|[;&|\n(])\s*git(?:\s+(?:-C\s+\S+|-c\s+\S+))*\s+add\s+([^;&|\n]*)")
MSG = re.compile(r"\s(?:-[A-Za-z]*m|--message[= ])\s*[\"']?(?:\$\(cat\s*<<-?\s*['\"]?\w+['\"]?\s*)?([^\n\"']*)")
SECRETS = [("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")), ("API key (sk-)", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
           ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")), ("GitHub token", re.compile(r"\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})")),
           ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"))]
JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.([A-Za-z0-9_-]{10,})\.[A-Za-z0-9_-]{10,}")

def added_lines(top, *args):
    """{path: [(line number, text)]} of the lines a diff adds."""
    out, cur, n, prev = {}, None, 0, ""
    for l in (ag.git(top, "diff", "-U0", "--no-color", *args) or "").splitlines():
        if l.startswith("+++ ") and prev.startswith("--- "):
            cur = l[6:] if l.startswith("+++ b/") else None  # +++ /dev/null: a deleted file
            if cur: out.setdefault(cur, [])
        elif l.startswith("@@"): n = int(re.search(r"\+(\d+)", l).group(1)) - 1
        elif l.startswith("+") and cur: n += 1; out[cur].append((n, l[1:]))
        prev = l
    return out

def pending(top, cmd):
    """What this commit would hold: the staged diff, plus the paths named by a `git add` earlier in the same command (it has not run yet)."""
    files = added_lines(top, "--cached")
    for spec in ADD.findall(cmd):
        try: paths = [a for a in shlex.split(spec) if not a.startswith("-")]
        except ValueError: continue
        if not paths: continue
        files.update(added_lines(top, "--", *paths))
        for p in (ag.git(top, "ls-files", "--others", "--exclude-standard", "-z", "--", *paths) or "").split("\0"):
            try: files[p] = list(enumerate(open(os.path.join(top, p), encoding="utf-8").read().splitlines(), 1)) if p and os.path.getsize(os.path.join(top, p)) < 1 << 20 else []
            except (OSError, UnicodeDecodeError): files[p] = []
    return files

def secret_hits(files):
    hits = []
    for path, lines in files.items():
        b = os.path.basename(path)
        if b == ".env" or (b.startswith(".env.") and b != ".env.example"): hits.append(f"{path} is an env file, keep it out of git")
        for n, t in lines:
            for label, rx in SECRETS:
                m = rx.search(t)
                if m: hits.append(f"{label} {ag.mask(m.group(0))} at {path}:{n}")
            for m in JWT.finditer(t):
                try: payload = base64.urlsafe_b64decode(m.group(1) + "===").decode("utf-8", "ignore")
                except Exception: payload = ""
                if len(m.group(0)) >= 80 and ("service_role" in t or "service_role" in payload): hits.append(f"service_role JWT {ag.mask(m.group(0))} at {path}:{n}")
    return hits

JS, PY = (".js", ".jsx", ".ts", ".tsx"), (".py",)
CLI_PATH = re.compile(r"(?:^|/)(?:scripts?|bin|cli|tools)/|(?:^|/)cli[\w.-]*$")
MOCK_PATH = re.compile(r"(?:^|/)(?:fixtures?|mocks?|__mocks__|stories|seeds?|examples?|docs?|e2e)/|\.stories\.|\.fixtures?\.")
LEFT = [  # (label, regex, extensions, skipped in command-line paths, skipped in test, fixture and story paths)
    ("console.log(", re.compile(r"\bconsole\.log\("), JS, True, True), ("debugger;", re.compile(r"^\s*debugger\s*;?\s*$"), JS, False, True),
    ("print( debugging", re.compile(r"^\s*print\("), PY, True, True), ("new TODO, FIXME or XXX", re.compile(r"\b(?:TODO|FIXME|XXX)\b"), ag.SRC, False, False),
    ("lorem ipsum", re.compile(r"lorem ipsum", re.I), ag.SRC, False, True), ("John Doe", re.compile(r"John Doe"), ag.SRC, False, True),
    ("a placeholder email", re.compile(r"example@example\.com|test@test\.com", re.I), ag.SRC, False, True),
    ("Math.random() as data", re.compile(r"(?:data|values?|scores?|prices?|amounts?|counts?|metrics?|series|stats?|revenue|users|views|total)\w*\s*[:=][^=].*Math\.random\(\)(?!\.toString)", re.I), JS, False, True),
    ("a hardcoded mock array", re.compile(r"\b(?:mock|fake|dummy)\w*\s*(?::[^=]+)?=\s*\[", re.I), JS + PY, False, True)]

def leftover_hits(top, files):
    """file:line of the added source lines that leave debugging output, TODOs or mock data behind (the Adams source holds these patterns itself and is skipped)."""
    hits, own = [], ag.is_adams_repo(top)
    for path, lines in files.items():
        low = path.lower()
        if not low.endswith(ag.SRC) or ag.SKIP & set(path.split("/")) or (own and path.startswith(("hooks/", "scripts/"))): continue
        testy = bool(ag.TESTY.search(path) or MOCK_PATH.search(path))
        for label, rx, exts, cli, quiet in LEFT:
            if not low.endswith(exts) or (cli and CLI_PATH.search(path)) or (quiet and testy): continue
            hits += [f"{label} at {path}:{n}" for n, t in lines if rx.search(t)][:3]
    return hits

def scope_hits(top, files, sid, cwd):
    globs = ag.scope_globs(top, sid, cwd)
    out = [p for p in files if globs and not ag.scope_ok(p, globs)]
    return [f"staged files outside the scope recorded for this session ({', '.join(globs)}): {', '.join(out[:5])}"] if out else []

def commit_message(cmd, cwd):
    m = MSG.search(cmd)
    if m: return m.group(1).strip()
    f = re.search(r"\s(?:-F|--file[= ])\s*(\S+)", cmd)
    try: return open(os.path.join(cwd, f.group(1)), encoding="utf-8").read().strip() if f else ""
    except OSError: return ""

def commit_gate(cmd, cwd, sid):
    """Reasons to deny this git commit (empty when it may go ahead)."""
    m = COMMIT.search(cmd)
    if ag.gates_off() or not m: return []
    base = ag.git_c(m.group(0), ag.cmd_base(cmd, cwd, m.start()))  # cd repo && git commit, git -C repo commit
    top = ag.git_top(base)
    if not top: return []
    files = pending(top, cmd)
    why = secret_hits(files)
    code = ag.source_files(list(files))
    msg = commit_message(cmd, base)
    if code and "--amend" not in cmd and not any(re.search(r"test|spec", p, re.I) for p in files):
        if re.match(r"fix(?:\(|:|!|\s|$)", msg, re.I): why.append("A bug fix needs a regression test in the same commit")
        elif re.match(r"(?:feat(?:\(|:|!|\s|$)|add\s|implement\s)", msg, re.I): why.append("A new feature needs a test in the same commit")
    cmds = ag.needs_verify(top, sid, cwd) if code else []
    if cmds: why.append("Code changed since the last green verification. Run " + ", ".join(cmds) + ", fix failures, then commit (run them in their own call, before the commit)")
    if code and os.environ.get("ADAMS_REVIEW") != "0":
        sp = ag.state_path("review", sid, cwd)
        if not ag.load(sp, {}).get("done"):
            ag.save(sp, {"done": True})  # denied once per session, the retry passes
            why.append("Review before commit: list in your next message, for the staged diff, in this order: correct, safe, holds under load, tested, fast, lean; fix anything that fails, then commit again")
    left = leftover_hits(top, files)
    return why + scope_hits(top, files, sid, cwd) + (["Leftovers in the staged lines, remove them first: " + "; ".join(left)] if left else [])

if __name__ == "__main__":
    try: d = json.load(sys.stdin); cmd = d.get("tool_input", {}).get("command", "")
    except Exception: sys.exit(0)  # never block on a malformed hook payload
    cwd = d.get("cwd") or os.getcwd()
    try: v = check(cmd, cwd) if not ag.gates_off() else check(cmd)
    except Exception: v = check(cmd)  # never block on an internal error in the extra checks
    if v:
        sys.stderr.write(f"Blocked by the Adams git guardrail: {v}. Ask the user to run it themselves if it is really needed.\n")
        sys.exit(2)
    try: why = commit_gate(cmd, d.get("cwd") or os.getcwd(), d.get("session_id"))
    except Exception: why = []  # never block on an internal error
    if why:
        sys.stderr.write("Blocked by the Adams commit gate: " + "; ".join(why) + ".\nOverride: the user sets ADAMS_GATES=0 (ADAMS_VERIFY=0 for the verification part only, ADAMS_REVIEW=0 for the review only), or runs the commit with the ! prefix.\n")
        sys.exit(2)
