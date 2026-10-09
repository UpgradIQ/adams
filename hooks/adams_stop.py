#!/usr/bin/env python3
"""Stop hook: runs the Adams text checks on the .md and .txt files this session wrote, and checks that code this session wrote was verified
(see adams_gates.py). "This session wrote" is the touched list that adams_verify_record.py keeps per session_id; files other sessions changed in the same folder
are never checked or reported, and a stop without a session_id or a touched list never blocks. Blocks the stop once when either check fails.
Files that passed the text check are remembered by content hash, so only edits are checked again.
Two more checks, each blocks once per session: a session aligned with `adams decide --small` that grew past 3 source files or 80 changed lines (align properly with the user), and a final message
with figures (percentages, 10x, 5 ms, N tests, "all tests pass", CLEAN, score N) that no command output of the session shows. Opt out with ADAMS_GATES=0 (ADAMS_STOP=0 for the figures too).
Never fails a session: any error exits 0 silently."""
import json, os, re, subprocess, sys, tempfile
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

def small_reason(data, mine):
    """A session whose only decisions were `adams decide --small` but whose touched source passed 3 files or 80 changed lines. Blocks once per session."""
    sid, cwd = data.get("session_id"), data.get("cwd") or os.getcwd()
    t0, sp = g.session_t0(sid, cwd, False), g.state_path("smallstop", sid, cwd)
    if g.gates_off() or not t0 or g.load(sp, {}).get("done"): return None
    for top in {t for t in (g.git_top(os.path.dirname(p)) for p in mine) if t}:
        notes = g.decisions_since(top, t0)
        if not notes or not all(n.startswith("small task:") for n in notes): continue
        rels = [r for r in g.source_files(g.changed_paths(top)[1]) if os.path.join(top, r) in mine]
        stat = [l.split("\t", 2) for l in (g.git(top, "diff", "--numstat", "HEAD", "--", *rels) or "").splitlines()] if rels else []
        seen = {x[2] for x in stat if len(x) == 3}
        lines = sum(int(a) + int(b) for a, b, _ in (x for x in stat if len(x) == 3) if a.isdigit() and b.isdigit())
        for r in rels:
            if r not in seen: lines += len(open(os.path.join(top, r), encoding="utf-8", errors="replace").read().splitlines())
        if len(rels) > 3 or lines > 80:
            g.save(sp, {"done": True})
            return (f"This session was recorded as a small task but it changed {len(rels)} source files and {lines} lines. Align properly now: ask the user the open decisions "
                    "(question tool, max 4 questions, each with your recommended option), then record them with `adams decide \"<decision>\"`. Override: the user sets ADAMS_GATES=0.")
    return None

FIG = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?:\s?%|x\b|\s?ms\b|\s+(?i:tests?|errors?|passed|failed)\b)|\b(\d+/\d+)\s+(?i:tests?\s+)?pass|\b[Ss]core\s+(\d+(?:\.\d+)?)\b|\b([Aa]ll tests? pass(?:ed|es|ing)?|FLAGGED 0|CLEAN)\b")

def transcript(path):
    """(text of the last assistant message, evidence): the command outputs and commands of the session plus the user's own words."""
    if not path or os.path.getsize(path) > 50 << 20: return "", ""
    bash, ev, last = set(), [], ""
    for raw in open(path, encoding="utf-8", errors="replace"):
        try: e = json.loads(raw)
        except ValueError: continue
        c = (e.get("message") or {}).get("content")
        for b in c if isinstance(c, list) else [{"type": "text", "text": c}] if isinstance(c, str) else []:
            if not isinstance(b, dict): continue
            if e.get("type") == "assistant" and b.get("type") == "text" and (b.get("text") or "").strip(): last = b["text"]
            elif b.get("type") == "tool_use" and b.get("name") == "Bash": bash.add(b.get("id")); ev.append((b.get("input") or {}).get("command") or "")
            elif b.get("type") == "tool_result" and b.get("tool_use_id") in bash:
                out = b.get("content"); ev.append(out if isinstance(out, str) else " ".join(x.get("text", "") for x in out or [] if isinstance(x, dict)))
            elif e.get("type") == "user" and b.get("type") == "text": ev.append(re.sub(r"<system-reminder>.*?</system-reminder>", "", b.get("text") or "", flags=re.S))  # the user's own words
    return last, "\n".join(ev)

def figures_reason(data):
    """Figures in the final message that no command output of this session shows. Blocks once per session."""
    sid, cwd = data.get("session_id"), data.get("cwd") or os.getcwd()
    sp = g.state_path("numstop", sid, cwd)
    if g.gates_off() or os.environ.get("ADAMS_STOP") == "0" or g.load(sp, {}).get("done"): return None
    last, ev = transcript(data.get("transcript_path"))
    green = any(r.get("ok") for r in g.load(g.state_path("verify", sid, cwd), []))
    bad = []
    for m in FIG.finditer(last):
        num, ratio, score, word = m.groups()
        if word: ok = (green or bool(re.search(r"pass", ev, re.I))) if word.lower().startswith("all") else word in ev  # CLEAN and FLAGGED 0 must appear in an output as written
        else:
            n = num or ratio or score
            ok = bool(re.search(r"(?<![\d.])" + re.escape(n.split("/")[0]) + r"(?!\d|\.\d)", ev)) or (green and (ratio is not None or (n == "0" and bool(re.search(r"error|failed", m.group(0))))))
        if not ok: bad.append(m.group(0).strip())
    if not bad: return None
    g.save(sp, {"done": True})
    return "Back every number with the command that produced it in this session, or remove it. Not shown by any command output: " + ", ".join(dict.fromkeys(bad)) + ". Override: the user sets ADAMS_GATES=0 (or ADAMS_STOP=0)."

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
    for f in (small_reason, figures_reason):
        try: reasons.append(f(data, mine) if f is small_reason else f(data))
        except Exception: pass
    reasons = [r for r in reasons if r]
    if reasons: print(json.dumps({"decision": "block", "reason": "\n\n".join(reasons)}))

if __name__ == "__main__":
    try: main()
    except Exception: pass
    sys.exit(0)
