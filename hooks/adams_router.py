#!/usr/bin/env python3
"""Context router. UserPromptSubmit (stdout becomes context) and PostToolUse / PostToolUseFailure (Edit, Write, MultiEdit, Bash; a write-like Bash command's source paths go through the same path rules; hookSpecificOutput.additionalContext).
Plain rules, no AI and no network: a prompt, an edited path or a failed test run selects a short Adams guidance block. Each rule fires at most once per session
(state file adams-router-<session_id> in the temp folder), at most two blocks per call, nothing is printed when no rule matches.
Opt out with ADAMS_GATES=0. Never fails a session: any error exits 0 silently."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adams_gates as g

TEXT = {
    "diagnose": "Adams diagnose: reproduce the failure first, then minimise it to the smallest input that still fails. Form one hypothesis at a time and test it with a probe (debugger, targeted log, failing test). "
                "No blind retries and no third guess without a feedback loop. Fix the root cause, add a regression test that failed before the fix, and say what the cause was. Detail: modules/workflow/references/diagnose.md (`adams where`).",
    "plain": "Adams plain language: restate your last answer short and plain, in the user's language (Egyptian Arabic if they wrote Arabic). No jargon, one idea per sentence, an everyday example if it helps, then the single next step. "
             "Professional terms stay in their original form. Do not repeat the long version.",
    "auth": "Adams security checklist for auth code: validate input at the boundary. Check authorization server-side on every action. No secrets in client code or logs. Rate limit auth endpoints. "
            "Compare secrets in constant time. Cookies: Secure, HttpOnly, SameSite. Row level security on every table touched. State which of these you checked.",
    "dependency": "Adams new dependency: before keeping it, ask whether the platform or an installed dependency already covers the need. Check what it costs (size, license, maintenance, last release). "
                  "State the cost to the user in your next message, and remove it if a few lines of your own code do the job.",
    "ui": "Adams UI check: before calling it done, run `adams check <url or file>` at 375, 768 and 1440 and quote the page and width coverage. Test long text, empty and error states, keyboard focus, and RTL where relevant.",
    "tests": "Adams tests first: write or update one failing test for the new behaviour, then implement it, and repeat (one test, one implementation). Tests check behaviour through public interfaces, not internals. "
             "Run the project's test command after each step.",
    "prose": "Adams published copy: make the minimum effective edit and keep the author's voice. List what changed in your next message. The Stop check (`adams check`) runs on the file automatically.",
}
ORDER = ("auth", "dependency", "tests", "ui", "prose", "diagnose", "plain")  # priority when several rules match one call
MAX_PER_CALL = 2

DIAGNOSE = re.compile(r"\b(?:broken|errors?|bugs?|failing|crash(?:es|ed|ing)?|not working|exceptions?|regression)\b|مش شغال|بايظ|خطأ|[اإ]يرور|مشكلة", re.I)
PLAIN = re.compile(r"مش فاهم|مش واضح|i don[’']?t understand|explain simply", re.I)
AUTH = re.compile(r"auth|session|login|signup|password|token|jwt|oauth|middleware|proxy|\.env|secret|permission|role|rls|polic(?:y|ies)", re.I)
UI = (".tsx", ".jsx", ".vue", ".svelte", ".css", ".scss", ".html")
CODE = tuple(e for e in g.SRC if e not in (".css", ".html", ".sh"))
TESTY = re.compile(r"(?:^|/)(?:tests?|__tests__|specs?|e2e)/|(?:^|/)test_[^/]*$|[._-](?:tests?|spec)\.\w+$|\.(?:test|spec)\.", re.I)
PROSE = re.compile(r"(?:^|/)(?:readme[^/]*|(?:docs?|posts?|blog|content|articles?|copy)/.*)$", re.I)
# one dependency per line, the group is its name (shortcut: line based, a bare name with no version inside a pyproject list is missed; add a TOML parse when that matters)
DEPS = {
    "package.json": re.compile(r'^\s*"((?!version"|name"|node"|npm"|pnpm"|yarn")@?[\w./-]+)"\s*:\s*"(?:[\^~<>=*]*\d[^"]*|\*|latest|workspace:[^"]*|npm:[^"]*|file:[^"]*|link:[^"]*|git[^"]*|github:[^"]*)"'),
    "requirements": re.compile(r"^\s*([A-Za-z0-9][\w.\-]*)(?:\[[\w,\- ]+\])?\s*(?:[<>=!~]=?[^#]*|;.*)?(?:#.*)?$"),
    "pyproject.toml": re.compile(r'"([A-Za-z][\w.\-]*)(?:\[[\w,]+\])?\s*[<>=!~]=?[^"]*"|^\s*(?!name\b|version\b|python\b|requires-python\b)([A-Za-z][\w.\-]*)\s*=\s*(?:"[\^~<>=*\d][^"]*"|\{[^}]*\bversion\b)'),
    "go.mod": re.compile(r"^\s*(?:require\s+)?([\w.\-]+\.[\w.\-]+/[\w./\-]+)\s+v\d"),
    "Cargo.toml": re.compile(r'^\s*(?!name\b|version\b|edition\b|rust-version\b|license\b|description\b|authors\b)([A-Za-z0-9_\-]+)\s*=\s*(?:"[\^~<>=*\d][^"]*"|\{[^}]*\b(?:version|git|path)\s*=)'),
}

def dep_kind(name):
    if name in DEPS: return name
    return "requirements" if re.fullmatch(r"requirements[\w.\-]*\.txt", name) else None

def dep_names(kind, text):
    out = set()
    for line in text.splitlines():
        if kind == "requirements" and line.strip().startswith("-"): continue
        out |= {next(x for x in m.groups() if x).lower() for m in DEPS[kind].finditer(line)}
    return out

def added_dependency(tool, ti, path, cwd):
    """True when this edit adds a dependency name that the old text did not have (Write: compared with git HEAD)."""
    kind = dep_kind(os.path.basename(path))
    if not kind: return False
    if tool == "Write":
        top = g.git_top(os.path.dirname(path))
        old = (g.git(top, "show", "HEAD:" + os.path.relpath(path, top)) or "") if top else ""
        return bool(dep_names(kind, ti.get("content") or "") - dep_names(kind, old))
    edits = ti.get("edits") if tool == "MultiEdit" else [ti]
    return any(dep_names(kind, e.get("new_string") or "") - dep_names(kind, e.get("old_string") or "") for e in edits or [])

def matched(data, st, rel_of):
    """Rule names selected by this payload."""
    hits = []
    tool, ti = data.get("tool_name") or "", data.get("tool_input") or {}
    if not tool and isinstance(data.get("prompt"), str):
        p = data["prompt"]
        if DIAGNOSE.search(p): hits.append("diagnose")
        if PLAIN.search(p): hits.append("plain")
        return hits
    cwd = data.get("cwd") or os.getcwd()
    if tool == "Bash":
        cmd, r = ti.get("command") or "", data.get("tool_response")
        code = next((r[k] for k in ("exit_code", "exitCode", "returncode", "code") if isinstance(r.get(k), int)), 0) if isinstance(r, dict) else 0
        if g.VERIFY.search(cmd) and (data.get("hook_event_name") == "PostToolUseFailure" or code != 0): hits.append("diagnose")
        # files a shell write names count like an Edit; tests first, so a test written beside its code counts
        for p in sorted(g.bash_targets(cmd, cwd), key=lambda x: (not TESTY.search(x), x)): hits += path_hits(tool, ti, p, st, rel_of, cwd)
        return hits
    p = ti.get("file_path")
    if tool not in ("Edit", "Write", "MultiEdit") or not isinstance(p, str): return hits
    return hits + path_hits(tool, ti, os.path.realpath(os.path.join(cwd, p)), st, rel_of, cwd)

def path_hits(tool, ti, p, st, rel_of, cwd):
    """Rule names selected by one written path (an Edit, Write or MultiEdit target, or a file a shell write names)."""
    hits = []
    rel = rel_of(p); low = rel.lower()
    if os.path.isabs(rel) or {".adams", ".planning"} & set(rel.split("/")): return hits  # outside the project, or Adams' own folders
    prose, is_test = low.endswith((".md", ".txt")), bool(TESTY.search(rel))
    if is_test: st["tests"] = True
    if not prose and AUTH.search(rel): hits.append("auth")
    if tool != "Bash" and added_dependency(tool, ti, p, cwd): hits.append("dependency")
    if low.endswith(UI): hits.append("ui")
    if prose and PROSE.search(rel): hits.append("prose")
    if low.endswith(CODE) and not is_test and not st.get("tests") and not g.SKIP & set(rel.split("/")):
        top = g.git_top(os.path.dirname(p))
        if top and g.detect_verify(top): hits.append("tests")
    return hits

def main():
    data = json.load(sys.stdin)
    if g.gates_off() or not isinstance(data, dict): return
    cwd = data.get("cwd") or os.getcwd()
    base = g.git_top(cwd) or os.path.realpath(cwd)
    rel_of = lambda p: os.path.relpath(p, base) if p.startswith(base + os.sep) else p
    sp = g.state_path("router", data.get("session_id"), cwd)
    st = g.load(sp, {})
    st.setdefault("fired", [])
    found = matched(data, st, rel_of)
    hits = [r for r in ORDER if r in found and r not in st["fired"]][:MAX_PER_CALL]
    st["fired"] += hits
    g.save(sp, st)
    if not hits: return
    text = "\n\n".join(TEXT[r] for r in hits)
    if data.get("tool_name"):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": data.get("hook_event_name") or "PostToolUse", "additionalContext": text}}))
    else: print(text)

if __name__ == "__main__":
    try: main()
    except Exception: pass
    sys.exit(0)
