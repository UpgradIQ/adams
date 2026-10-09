#!/usr/bin/env python3
"""PreToolUse hook (Edit, Write, MultiEdit, NotebookEdit, and Bash for write-like and delete commands): the agent deviation gates. One denial lists every reason.
  test tampering   a test file gets .skip( / .only( / xit( / pytest.skip and the like, is deleted or emptied, or loses assertions net
  silencing        @ts-ignore, @ts-nocheck, a bare @ts-expect-error, eslint-disable, # type: ignore, # noqa, //nolint, a new `any`, or a config that loosens strictness
  gaming checks    CI workflows, coverage and budget thresholds, snapshots, scripts/selftest.py outside the Adams repo; open only after the user's prompt named ci, workflow, threshold, snapshot or selftest
  self-disabling   ADAMS_GATES=0 and its siblings in a command, and writes to the user's Claude and Adams config, CLAUDE.md and the plugin cache (the Adams source itself may be edited)
  scope            after `adams decide --scope "glob,glob"` a write outside the globs is denied (tests, docs and .adams stay open)
Opt out with ADAMS_GATES=0 set by the user before starting Claude Code. Never blocks on an internal error."""
import json, os, re, shlex, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adams_gates as g

SKIPS = re.compile(r"\.skip\(|\.only\(|\bxit\(|\bxtest\(|\bxdescribe\(|\bit\.todo\b|@pytest\.mark\.skip(?!if)|\bpytest\.skip\(|@unittest\.skip|\bt\.Skip\(|#\[ignore\]")
ASSERT = re.compile(r"\bassert\w*\s*[(.]|\bassert\s+[\w(\[\"'-]|\bexpect\(|\bshould\.|\.should\(|\brequire\.\w+\(")
SILENCE = [(n, re.compile(r)) for n, r in [("@ts-ignore", r"@ts-ignore"), ("@ts-nocheck", r"@ts-nocheck"), ("@ts-expect-error without a written reason", r"@ts-expect-error(?![ \t]*[:\-]?[ \t]*\S.{9,})"),
           ("eslint-disable", r"eslint-disable"), ("# type: ignore", r"#\s*type:\s*ignore"), ("# noqa", r"#\s*noqa\b"), ("//nolint", r"//\s*nolint\b")]]
ANY = re.compile(r":\s*any\b|\bas\s+any\b")
LOOSE = [(re.compile(r"(?:^|/)tsconfig[\w.-]*\.json$"), re.compile(r'"(?:strict\w*|noImplicit\w+|noUnused\w+|alwaysStrict|exactOptionalPropertyTypes)"\s*:\s*false')),
         (re.compile(r"(?:^|/)(?:\.eslintrc[\w.]*|eslint\.config\.\w+)$"), re.compile(r"""["']off["']|["']?[\w@/.-]+["']?\s*:\s*0\b|ignorePatterns|\bignores\s*:""")),
         (re.compile(r"(?:^|/)(?:\.?ruff\.toml|\.?mypy\.ini|pyproject\.toml|setup\.cfg|tox\.ini|\.flake8)$"),
          re.compile(r"\b(?:extend-)?ignore\s*=|per-file-ignores|\bignore_errors\s*=\s*true|\bignore_missing_imports\s*=\s*true|\b(?:strict|disallow_\w+|check_untyped_defs|warn_\w+)\s*=\s*false", re.I))]
ALWAYS = re.compile(r"(?:^|/)(?:\.github/workflows/[^/]+\.ya?ml|\.gitlab-ci\.yml|\.circleci/config\.yml|\.nycrc[\w.]*|\.c8rc[\w.]*|\.coveragerc|\.?codecov\.ya?ml|\.?lighthouserc[\w.]*|budgets?\.json|\.adams/config\.json|__snapshots__/.*|[^/]+\.snap)$")
CONF = re.compile(r"(?:^|/)(?:(?:jest|vitest|playwright)\.config\.\w+|package\.json|pyproject\.toml|setup\.cfg|tox\.ini|pytest\.ini)$")
THRESH = re.compile(r"thresholds?|coverage|budget|fail[_-]under|min[_-]?(?:score|coverage)|\bbranches\b|\bstatements\b", re.I)
SNAPSHOT_RUN = re.compile(r"\b(?:jest|vitest)\b[^;&|\n]*\s(?:-u|--update\w*)\b|--snapshot-update|--update-snapshots?\b")
ENV_OFF = re.compile(r"\bADAMS_(?:GATES|VERIFY|STOP|REVIEW)=[\"']?0")
HOOKISH = re.compile(r"hooks|PreToolUse|PostToolUse|UserPromptSubmit|SessionStart|\"command\"|disableAllHooks|enabledPlugins|ADAMS_")
SUBST = re.compile(r"\bs([/|#,:@])(?:(?!\1).|\\\1)*\1((?:(?!\1).|\\\1)*)\1")  # sed or perl s/old/new/: group 2 is the replacement
FIX_TEST = "Tests are the referee: fix the code, not the test."
testy = lambda s: bool(g.TESTY.search(s) or g.TESTY.search(s + "/"))

def read(p):
    try: return open(p, encoding="utf-8", errors="replace").read() if os.path.getsize(p) < 2 << 20 else ""
    except OSError: return ""

def changes(data, cwd):
    """[(realpath, old, new, whole)] this call writes. old is the text before (None when unknown, as for a shell command), new the text after, whole is True when new replaces the whole file.
    Edit and MultiEdit give the replaced and the new snippets; a shell write gives the replacement parts of sed and perl substitutions, else the whole command (heredocs included)."""
    tool, ti = data.get("tool_name"), data.get("tool_input") or {}
    if tool == "Bash":
        cmd = ti.get("command") or ""
        new = "\n".join(m.group(2) for m in SUBST.finditer(cmd)) if re.search(r"\b(?:sed|perl)\s+-[\w-]*i", cmd) else cmd
        return [(p, None, new, False) for p in sorted(g.bash_targets(cmd, cwd, True)) if os.path.exists(p) or os.path.splitext(p)[1] or os.path.basename(p).startswith(".")]
    p = ti.get("file_path") or ti.get("notebook_path")
    if not isinstance(p, str): return []
    p = os.path.realpath(os.path.join(cwd, p))
    if tool == "Write": return [(p, read(p), ti.get("content") or "", True)]
    if tool == "NotebookEdit": return [(p, "", ti.get("new_source") or "", False)]
    es = [e for e in (ti.get("edits") if tool == "MultiEdit" else [ti]) or [] if isinstance(e, dict)]
    return [(p, "\n".join(e.get("old_string") or "" for e in es), "\n".join(e.get("new_string") or "" for e in es), False)]

def deletions(cmd, cwd):
    """Realpaths that rm, unlink, rmdir, git rm and mv take away (a move into another test path is a rename and is left out)."""
    base, out = cwd, []
    for m in re.finditer(r"\bcd\s+[\"']?([^\s;&|\"']+)", cmd): base = os.path.join(base, os.path.expanduser(m.group(1)))
    for seg in re.split(r"&&|\|\||;|\n|\|", cmd):
        try: t = shlex.split(seg)
        except ValueError: t = seg.split()
        while t and re.fullmatch(r"[A-Za-z_]\w*=.*", t[0]): t = t[1:]
        if t[:1] == ["git"]: t = t[1:]
        if not t or t[0] not in ("rm", "unlink", "rmdir", "mv"): continue
        args = [a for a in t[1:] if not a.startswith("-")]
        if t[0] == "mv": args = args[:-1] if len(args) > 1 and not testy(args[-1]) else []
        out += [os.path.realpath(os.path.join(base, os.path.expanduser(a))) for a in args]
    return out

def grew(rx, old, new): return len(rx.findall(new)) > (len(rx.findall(old)) if old is not None else 0)

def symdiff(old, new):
    a, b = (old or "").splitlines(), new.splitlines()
    return "\n".join([l for l in a if l not in b] + [l for l in b if l not in a])

def protected(p, text):
    """What of the user's p is (Claude and Adams config, CLAUDE.md, the plugin copy, the hooks of a project settings file), or None."""
    h = os.path.realpath(os.path.expanduser("~"))
    under = lambda d: p == d or p.startswith(d + os.sep)
    if p in (h + "/CLAUDE.md", h + "/.claude/CLAUDE.md"): return "a CLAUDE.md file"
    if os.path.dirname(p) == h + "/.claude" and re.fullmatch(r"settings[\w.-]*\.json", os.path.basename(p)): return "the Claude Code user settings"
    if under(h + "/.config/adams"): return "the Adams config and profiles"
    if under(h + "/.claude/plugins"): return "the installed plugin copy"
    if re.search(r"(?:^|/)\.claude/settings[\w.-]*\.json$", p) and HOOKISH.search(text): return "the hooks of a Claude Code settings file"
    return None

def judge(p, old, new, whole, gone, top, rel, asked, globs):
    """Reasons to deny one write (or, with gone, one deletion) of p."""
    why, base = [], os.path.basename(p)
    own = g.is_adams_repo(top) and rel.startswith(("hooks/", "scripts/"))  # the Adams source holds the patterns it detects
    if not own:
        if gone and testy(rel): why.append("it deletes a test file or test folder. " + FIX_TEST)
        if testy(rel) and rel.lower().endswith(g.SRC):
            if grew(SKIPS, old, new): why.append("it adds a skip or only marker (.skip(, .only(, xit(, pytest.skip, t.Skip, #[ignore]) to a test file. " + FIX_TEST)
            if whole and old.strip() and not new.strip(): why.append("it empties a test file. " + FIX_TEST)
            if old is not None and len(ASSERT.findall(new)) < len(ASSERT.findall(old)): why.append(f"it removes assertions from a test file net ({len(ASSERT.findall(old))} to {len(ASSERT.findall(new))}). " + FIX_TEST)
        if rel.lower().endswith(g.SRC):
            hit = [n for n, rx in SILENCE if grew(rx, old, new)] + (["a new `any`"] if rel.lower().endswith((".ts", ".tsx")) and grew(ANY, old, new) else [])
            if hit: why.append("it silences an error (" + ", ".join(hit) + "). Fix the cause; if it is truly unavoidable, ask the user and give the written reason")
        why += [f"it loosens {base} (strictness off, a rule disabled or an ignore list grown). Ask the user, with the reason" for name, rx in LOOSE if name.search(rel) and grew(rx, old, new)]
    ref = bool(ALWAYS.search(rel)) or (rel == "scripts/selftest.py" and not g.is_adams_repo(top))
    if not ref and CONF.search(rel) and not gone:
        ch = symdiff(old, new)
        ref = bool(THRESH.search(ch)) or (bool(THRESH.search(read(p))) and bool(re.search(r"\d", ch)) and not base.startswith(("package.json", "pyproject")))
    if ref and not asked: why.append("it changes a referee (CI, thresholds, snapshots or the project's own check script). Ask the user before changing it")
    if globs and not g.scope_ok(rel, globs): why.append(f"it is outside the scope recorded for this session ({', '.join(globs)})")
    return why

def main():
    data = json.load(sys.stdin)
    if g.gates_off() or not isinstance(data, dict): return
    cwd, sid = data.get("cwd") or os.getcwd(), data.get("session_id")
    g.session_t0(sid, cwd)  # the session's first call fixes its start, which scope and small-task detection compare with
    cmd = (data.get("tool_input") or {}).get("command") or "" if data.get("tool_name") == "Bash" else ""
    asked = g.load(g.state_path("router", sid, cwd), {}).get("asked") if sid else None  # referee words the user's prompts used
    tops, why = {}, []
    def top_of(p):
        d = os.path.dirname(p)
        if d not in tops: tops[d] = g.git_top(d)
        return tops[d]
    if cmd and ENV_OFF.search(cmd) and not g.is_adams_repo(g.git_top(cwd)): why.append("the command turns an Adams gate off (ADAMS_GATES=0 and its siblings). Only the user can switch Adams off")
    if cmd and SNAPSHOT_RUN.search(cmd) and not asked: why.append("the command rewrites snapshots. Ask the user before updating the referee")
    gone = {p for p in deletions(cmd, cwd)} if cmd else set()
    for p, old, new, whole in changes(data, cwd) + [(p, None, "", False) for p in sorted(gone)]:
        top = top_of(p)
        what = protected(p, (old or "") + "\n" + new)
        if what:  # the Adams source repo may edit its own settings and config files
            if not g.is_adams_repo(top): why.append(f"{p} is {what}. Only the user can change it")
            continue
        if not top: continue
        rel = os.path.relpath(p, top)
        if p in gone and not g.git(top, "ls-files", "--", rel): continue  # only a tracked path counts as taken away
        why += [f"{rel}: {x}" for x in judge(p, old, new, whole, p in gone, top, rel, asked, g.scope_globs(top, sid, cwd))]
    if why:
        g.deny("Adams deviation gate: " + "; ".join(dict.fromkeys(w.rstrip(".") for w in why)) + ". Override: the user sets ADAMS_GATES=0 before starting Claude Code (referee files also open once the user's prompt names ci, workflow, threshold, snapshot or selftest).")

if __name__ == "__main__":
    try: main()
    except Exception: pass
    sys.exit(0)
