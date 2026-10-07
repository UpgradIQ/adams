#!/usr/bin/env python3
"""Track tooling for the SaaS revamp program (stdlib only).
  python3 track.py lint FILE            validate .planning/track.md format, exit 1 on errors
  python3 track.py render FILE OUT.html render a clean light/dark HTML checklist (no external assets)
  python3 track.py selftest             assert-based checks on an embedded sample
Format: modules/senior-frontend/references/execution.md and track-template.md."""
import html, os, re, sys, tempfile

STATUSES = ("todo", "in-progress", "blocked", "review", "done", "verified", "dropped")
OPEN = ("todo", "in-progress", "blocked", "review")
VERDICTS = ("Ready", "Ready with gaps", "Not ready")
FIELDS = ("id", "title", "phase", "status", "evidence", "definition of done", "risks", "next action", "agent prompt")
DASHES = (chr(0x2014), chr(0x2013))


def parse(text):
    """Return (data, errors). data: header, next, phases, tasks."""
    errs, header, nxt, phases, tasks = [], {}, [], [], []
    sec, cur = None, None  # section name, current phase/task dict
    lastkey = None
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if line.startswith("## "):
            sec, cur, lastkey = line[3:].strip().lower(), None, None
            continue
        if line.startswith("### ") and sec in ("phases", "tasks"):
            parts = line[4:].strip().split(None, 1)
            cur = {"id": parts[0] if parts else "", "name": parts[1] if len(parts) > 1 else "", "line": n, "f": {}, "purpose": []}
            (phases if sec == "phases" else tasks).append(cur)
            lastkey = None
            continue
        if sec is None:
            m = re.match(r"^(project|updated|verdict):\s*(.*)$", line, re.I)
            if m: header[m.group(1).lower()] = m.group(2).strip()
        elif sec == "next immediate task":
            if line.strip() and not line.strip().startswith("<!--"): nxt.append(line.strip())
        elif sec == "phases" and cur is not None and line.strip():
            cur["purpose"].append(line.strip())
        elif sec == "tasks" and cur is not None:
            m = re.match(r"^- ([A-Za-z ]+):\s*(.*)$", line)
            if m: lastkey = m.group(1).strip().lower(); cur["f"][lastkey] = m.group(2).strip()
            elif line.startswith("  ") and lastkey and line.strip(): cur["f"][lastkey] += " " + line.strip()
    return {"header": header, "next": nxt, "phases": phases, "tasks": tasks}, errs


def lint_text(text):
    d, errs = parse(text)
    if any(c in text for c in DASHES): errs.append("em dash or en dash found; use comma, colon, parentheses or a middle dot")
    for k in ("project", "updated", "verdict"):
        if not d["header"].get(k): errs.append(f"header: missing '{k.capitalize()}:'")
    if d["header"].get("updated") and not re.match(r"^\d{4}-\d{2}-\d{2}$", d["header"]["updated"]): errs.append("header: Updated must be YYYY-MM-DD")
    v = d["header"].get("verdict")
    if v and v not in VERDICTS: errs.append(f"header: Verdict must be one of {', '.join(VERDICTS)}")
    if not d["phases"]: errs.append("no phases (### P1 Name under '## Phases')")
    if not d["tasks"]: errs.append("no tasks (### T-001 Title under '## Tasks')")
    pids = {p["id"] for p in d["phases"]}
    if len(pids) != len(d["phases"]): errs.append("duplicate phase ids")
    ids, byid = [], {}
    for t in d["tasks"]:
        f, tid = t["f"], t["id"]
        ids.append(tid); byid[tid] = t
        for k in FIELDS:
            if k not in f: errs.append(f"{tid}: missing field '{k}'")
        for k in ("evidence", "definition of done"):
            if k in f and not f[k].strip(): errs.append(f"{tid}: '{k}' is empty")
        if f.get("id") and f["id"] != tid: errs.append(f"{tid}: field id '{f['id']}' differs from heading")
        if f.get("status") and f["status"] not in STATUSES: errs.append(f"{tid}: status '{f['status']}' not in {', '.join(STATUSES)}")
        if f.get("phase") and f["phase"] not in pids: errs.append(f"{tid}: phase '{f['phase']}' does not exist")
    if len(set(ids)) != len(ids): errs.append("duplicate task ids")
    open_ids = [t["id"] for t in d["tasks"] if t["f"].get("status") in OPEN]
    if not d["next"]:
        errs.append("'## Next immediate task' is empty (exactly one task required)")
    elif len(d["next"]) != 1:
        errs.append(f"'## Next immediate task' must hold exactly one line, found {len(d['next'])}")
    else:
        first = d["next"][0].split()[0].rstrip(":,.")
        if first.lower() == "none":
            if open_ids: errs.append("Next immediate task says none but open tasks exist: " + ", ".join(open_ids))
        elif first not in byid: errs.append(f"Next immediate task '{first}' is not a task id")
        elif byid[first]["f"].get("status") not in ("todo", "in-progress"): errs.append(f"Next immediate task {first} must be todo or in-progress")
    if v == "Ready":
        bad = [t["id"] for t in d["tasks"] if t["f"].get("status") not in ("verified", "dropped")]
        if bad: errs.append("Verdict Ready needs every task verified or dropped; not so: " + ", ".join(bad))
    return errs


def lint(path):
    errs = lint_text(open(path, encoding="utf-8").read())
    for e in errs: print("ERROR", e)
    print(f"track lint: {len(errs)} error(s)" if errs else "track lint OK")
    return 1 if errs else 0


CSS = """:root{--bg:#fff;--fg:#14110a;--mu:#5d5a52;--bd:#e3e0d6;--card:#faf9f5;--ac:#7a5d00;--fill:#fcd535;--ok:#1a6b3a;--bad:#a02323}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#12110d;--fg:#f4f1e6;--mu:#a8a493;--bd:#2f2d25;--card:#1a1913;--ac:#fcd535;--fill:#fcd535;--ok:#5fd08a;--bad:#ff8a8a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#12110d;--fg:#f4f1e6;--mu:#a8a493;--bd:#2f2d25;--card:#1a1913;--ac:#fcd535;--fill:#fcd535;--ok:#5fd08a;--bad:#ff8a8a;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1100px;margin:0 auto;padding:32px 16px 64px}h1{font-size:28px;margin:0 0 4px}h2{font-size:20px;margin:0}
.mu{color:var(--mu)}.meta{display:flex;flex-wrap:wrap;gap:8px 24px;margin:8px 0 24px}
.next{border:1.5px solid var(--bd);background:var(--card);border-radius:16px;padding:16px;margin:0 0 24px}.next b{display:block;font-size:13px;color:var(--mu);text-transform:uppercase;letter-spacing:.04em}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 24px}button{font:inherit;border:1.5px solid var(--bd);background:var(--bg);color:var(--fg);border-radius:100px;padding:6px 14px;min-height:36px;cursor:pointer}
button[aria-pressed=true]{background:var(--fill);color:#14110a;border-color:var(--fill)}button:focus-visible,summary:focus-visible{outline:3px solid var(--ac);outline-offset:2px}
section.phase{border:1.5px solid var(--bd);border-radius:16px;padding:16px;margin:0 0 16px}.ph{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px}
.bar{height:10px;border-radius:100px;background:var(--bd);overflow:hidden;margin:8px 0 16px}.bar i{display:block;height:100%;background:var(--fill)}
ul{list-style:none;margin:0;padding:0}li.task{border-top:1px solid var(--bd);padding:8px 0}li.task[hidden]{display:none}
summary{cursor:pointer;display:flex;flex-wrap:wrap;gap:8px;align-items:center}.id{font-family:ui-monospace,monospace;font-size:13px;color:var(--mu)}
.st{font-size:12px;border:1.5px solid var(--bd);border-radius:100px;padding:1px 10px}.st.verified,.st.done{border-color:var(--ok);color:var(--ok)}.st.blocked{border-color:var(--bad);color:var(--bad)}.st.in-progress,.st.review{border-color:var(--ac);color:var(--ac)}
dl{display:grid;grid-template-columns:160px 1fr;gap:4px 16px;margin:8px 0 0}dt{color:var(--mu)}dd{margin:0}
@media(max-width:600px){dl{grid-template-columns:1fr}}"""

JS = """const bs=document.querySelectorAll('.filters button'),ts=document.querySelectorAll('li.task'),live=document.getElementById('count');
bs.forEach(b=>b.addEventListener('click',()=>{bs.forEach(x=>x.setAttribute('aria-pressed',x===b));const f=b.dataset.f;let n=0;
ts.forEach(t=>{const s=f==='all'||t.dataset.s===f;t.hidden=!s;if(s)n++});live.textContent=n+' task'+(n===1?'':'s')+' shown'}));"""


def render_html(text):
    d, _ = parse(text)
    e = html.escape
    tasks = d["tasks"]
    counts = {s: sum(1 for t in tasks if t["f"].get("status") == s) for s in STATUSES}
    h = d["header"]
    out = [f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{e(h.get('project', 'Project'))} tracker</title><style>{CSS}</style></head><body><main>",
           f"<h1>{e(h.get('project', 'Project'))} tracker</h1><div class=\"meta mu\"><span>Updated {e(h.get('updated', ''))}</span><span>Verdict: <b>{e(h.get('verdict', ''))}</b></span><span>{len(tasks)} tasks</span></div>",
           f"<div class=\"next\"><b>Next immediate task</b>{e(' '.join(d['next']))}</div>",
           "<div class=\"filters\" role=\"group\" aria-label=\"Filter by status\"><button type=\"button\" data-f=\"all\" aria-pressed=\"true\">All " + str(len(tasks)) + "</button>"
           + "".join(f"<button type=\"button\" data-f=\"{s}\" aria-pressed=\"false\">{s} {counts[s]}</button>" for s in STATUSES) + "</div>",
           f"<p class=\"mu\" id=\"count\" aria-live=\"polite\">{len(tasks)} tasks shown</p>"]
    for p in d["phases"]:
        pt = [t for t in tasks if t["f"].get("phase") == p["id"]]
        live_ = [t for t in pt if t["f"].get("status") != "dropped"]
        done = sum(1 for t in live_ if t["f"].get("status") in ("done", "verified"))
        pct = round(100 * done / len(live_)) if live_ else 0
        out.append(f"<section class=\"phase\"><div class=\"ph\"><h2>{e(p['id'])} {e(p['name'])}</h2><span class=\"mu\">{done} of {len(live_)} done</span></div>"
                   f"<div class=\"bar\" role=\"progressbar\" aria-label=\"{e(p['id'])} progress\" aria-valuemin=\"0\" aria-valuemax=\"100\" aria-valuenow=\"{pct}\"><i style=\"width:{pct}%\"></i></div><ul>")
        for t in pt:
            f = t["f"]; s = f.get("status", "")
            rows = "".join(f"<dt>{e(k.capitalize())}</dt><dd>{e(f.get(k, ''))}</dd>" for k in ("evidence", "definition of done", "risks", "next action", "agent prompt"))
            out.append(f"<li class=\"task\" data-s=\"{e(s)}\"><details><summary><span class=\"id\">{e(t['id'])}</span><span>{e(t['name'])}</span><span class=\"st {e(s)}\">{e(s)}</span></summary><dl>{rows}</dl></details></li>")
        out.append("</ul></section>")
    out.append(f"</main><script>{JS}</script></body></html>")
    return "".join(out)


def render(path, outpath):
    text = open(path, encoding="utf-8").read()
    page = render_html(text)
    assert not any(c in page for c in DASHES), "dash in rendered page"
    open(outpath, "w", encoding="utf-8").write(page)
    print(f"rendered {outpath}")
    return 0


SAMPLE = """# Track: Sample SaaS
Project: Sample SaaS
Updated: 2026-10-06
Verdict: Not ready

## Next immediate task
T-002 Fix the connector connected state

## Phases
### P1 Audit
Score the running product with runtime evidence.
### P2 Execute
Ship one task at a time.

## Tasks
### T-001 Score the dashboard
- id: T-001
- title: Score the dashboard
- phase: P1
- status: verified
- evidence: /dashboard renders 6 equal tiles, 9 open items on home (screenshot at 1280)
- definition of done: 12 lenses scored with runtime evidence; issues recorded
- risks: none
- next action: none
- agent prompt: Execute only T-001. Mark verified only if every item in the definition of done holds.

### T-002 Fix the connector connected state
- id: T-002
- title: Fix the connector connected state
- phase: P2
- status: todo
- evidence: /settings/integrations shows Connected beside an empty property field
- definition of done: connected state shows last read time, 3 real values, what it unlocked, Test now and Reconnect
- risks: source API rate limit
- next action: read the connector component and its states
- agent prompt: Execute only T-002. Update track.md. Mark done only if every item in the definition of done holds.
"""


def selftest():
    assert lint_text(SAMPLE) == [], lint_text(SAMPLE)
    bad = lambda s, frag: any(frag in x for x in lint_text(s))
    assert bad(SAMPLE.replace("status: todo", "status: wip"), "status 'wip'")
    assert bad(SAMPLE.replace("T-002 Fix the connector connected state\n\n## Phases", "T-002 a\nT-001 b\n\n## Phases"), "exactly one")
    assert bad(SAMPLE.replace("- evidence: /settings/integrations shows Connected beside an empty property field", "- evidence:"), "'evidence' is empty")
    assert bad(SAMPLE.replace("- definition of done: connected state shows last read time, 3 real values, what it unlocked, Test now and Reconnect\n", ""), "missing field 'definition of done'")
    assert bad(SAMPLE.replace("Not ready", "Ready"), "Verdict Ready")
    assert bad(SAMPLE.replace("Score the running", "Score the " + chr(0x2014) + " running"), "dash")
    assert bad(SAMPLE.replace("T-002 Fix the connector connected state\n\n## Phases", "T-001 Score\n\n## Phases"), "must be todo or in-progress")
    page = render_html(SAMPLE)
    assert "P1 Audit" in page and "P2 Execute" in page and 'data-f="verified"' in page and "1 of 1 done" in page
    assert not any(c in page for c in DASHES) and "http" not in page.replace("<!doctype html>", "")
    d = tempfile.mkdtemp(prefix="track-selftest-")
    try:
        f, o = os.path.join(d, "track.md"), os.path.join(d, "t.html")
        open(f, "w", encoding="utf-8").write(SAMPLE)
        assert lint(f) == 0 and render(f, o) == 0 and os.path.getsize(o) > 1000
    finally:
        for x in os.listdir(d): os.remove(os.path.join(d, x))
        os.rmdir(d)
    print("track selftest OK")
    return 0


def main(a):
    if a[:1] == ["lint"] and len(a) == 2: return lint(a[1])
    if a[:1] == ["render"] and len(a) == 3: return render(a[1], a[2])
    if a == ["selftest"]: return selftest()
    print(__doc__); return 2


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
