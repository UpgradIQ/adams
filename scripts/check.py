#!/usr/bin/env python3
"""Adams check: one command that picks the right checks for each input.
Usage: python3 check.py FILE_OR_URL [...]      exit 1 if any check flags something.
  .txt .md   hzlint (--reply for reply/dm names, --doc if it has # headings, --msa for AR/MSA names or playbooks) + arlint if Arabic
  .pdf       line_balance + title_check
  .pptx      textlint (speaker notes and text), then rendered to PDF and checked like a PDF
  .docx      rendered to PDF with LibreOffice (soffice), then checked like a PDF
  .html      served on a temporary local port (from the site root when the page uses /root-relative links), then web_balance at 375/768/1440 (crawls its in-page hash routes too)
             page checks at every width: PLACEHOLDER COUNT GAP GAP-RHYTHM TABLE SUBLINE THIN A11Y BROKEN COPY COVER RTL (see modules/line-balance/GUIDE.md)
  http(s)    web_balance --crawl --max 10 (override with extra flags after --)
             a URL with a #fragment (http://localhost:4330/#/view) is scanned at exactly that fragment and not crawled; without one it crawls
             both run web_balance --stress (longer text, long tokens, big numbers, empty lists at 375 and 1440); skip with  -- --no-stress
  --changed        check only the files changed in this git repo (staged, unstaged and new)
  --since REF      check only the files changed since REF (a branch, tag or commit), plus the working tree
The verdict reports coverage: ADAMS CHECK: CLEAN (2 files, 3 pages x 3 widths, WARNING ...). WARNING lines never change the exit code.
Dependencies install themselves on first run (see the scripts)."""
import importlib.util, json, os, re, shutil, socket, subprocess, sys, tempfile, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = lambda *p: os.path.join(ROOT, "modules", *p)
PY = sys.executable
AR = re.compile("[؀-ۿ]")

def run(label, cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    print(f"--- {label} (exit {r.returncode})\n{out[-6000:]}")
    LAST[0] = out
    return r.returncode

TEXT_SEEN = False
LAST = [""]  # full output of the last run()
COVER = {"files": 0, "pages": 0, "widths": set(), "warn": [], "hits": {}}  # what the verdict reports as covered

def profile_groups():
    spec = importlib.util.spec_from_file_location("hz", M("humanize-writing", "scripts", "hzlint.py"))
    hz = importlib.util.module_from_spec(spec); spec.loader.exec_module(hz)
    return hz.load_profile()[1]

def text_file(f):
    global TEXT_SEEN
    TEXT_SEEN = True; COVER["files"] += 1
    t = open(f, encoding="utf-8", errors="ignore").read(); n = os.path.basename(f).lower(); flags = []
    if re.search(r"(?<![a-z])(reply|dm|comment)(?![a-z])", n): flags.append("--reply")
    elif re.search(r"^#{1,3} ", t, re.M): flags.append("--doc")
    if re.search(r"-ar\b|_ar\b|playbook|msa", n): flags.append("--msa")
    rc = run("hzlint " + " ".join(flags), [PY, M("humanize-writing", "scripts", "hzlint.py"), *flags, f])
    if AR.search(t) and profile_groups().get("arabic_style"): rc |= run("arlint", [PY, M("deliverable-visual-qa", "scripts", "arlint.py"), f])
    return rc

def pdf_checks(x):
    return (run("line_balance", [PY, M("line-balance", "scripts", "line_balance.py"), x])
            | run("title_check", [PY, M("deliverable-visual-qa", "scripts", "title_check.py"), x]))

def office_to_pdf(x):
    """Render docx/pptx to PDF with LibreOffice; returns (pdf_path, tmpdir) or (None, None) with a message."""
    soffice = shutil.which("soffice")
    if not soffice: print(f"--- skip render of {x}: LibreOffice (soffice) not installed, run `brew install --cask libreoffice`"); return None, None
    d = tempfile.mkdtemp(prefix="adams-")
    try:
        subprocess.run([soffice, f"-env:UserInstallation=file://{d}/profile", "--headless", "--convert-to", "pdf", "--outdir", d, x], capture_output=True, timeout=180)
    except subprocess.TimeoutExpired: print(f"--- skip render of {x}: soffice timed out")
    pdf = os.path.join(d, os.path.splitext(os.path.basename(x))[0] + ".pdf")
    return (pdf, d) if os.path.exists(pdf) else (None, d)

def web(url, extra, stress=True):
    rc = run("web_balance " + url, ["node", M("line-balance", "scripts", "web_balance.js"), "--base", url, *extra, *(["--stress"] if stress else [])])
    m = re.search(r"^PAGES (\d+)\s+WIDTHS ([\d,]+)", LAST[0], re.M)
    if m: COVER["pages"] += int(m.group(1)); COVER["widths"] |= set(m.group(2).split(","))
    COVER["warn"] += [w for w in re.findall(r"^WARNING (.+)$", LAST[0], re.M) if w not in COVER["warn"]]
    m = re.search(r"^PAGES .*?(\{.*\})$", LAST[0], re.M)
    if m:
        for k, v in json.loads(m.group(1)).items(): COVER["hits"][k] = COVER["hits"].get(k, 0) + v
    return rc

def coverage():
    """The verdict states what was scanned: a single-page app checked as one page must not read as a pass."""
    c, parts = COVER, []
    if c["files"]: parts.append(f"{c['files']} file{'s' * (c['files'] > 1)}")
    if c["pages"]: parts.append(f"{c['pages']} page{'s' * (c['pages'] > 1)} x {len(c['widths'])} widths")
    for w in c["warn"]: print("WARNING " + w); parts.append("WARNING " + re.sub(r" \(use .*\)$", "", w))
    return f" ({', '.join(parts)})" if parts else ""

def serve_root(x):
    """Folder to serve a page from. A page that links /root-relative files (/_astro/a.css) only works when the server root is the site root,
    so walk up from the page to the folder where its first /root-relative files exist (a dist/ build checked page by page)."""
    d = os.path.dirname(os.path.abspath(x))
    refs = [r for r in re.findall(r'(?:href|src)="(/[^/"#?][^"#?]*\.\w+)"', open(x, encoding="utf-8", errors="ignore").read())[:8]]
    up = d
    for _ in range(6):
        if any(os.path.isfile(os.path.join(up, r.lstrip("/"))) for r in refs): return up
        if os.path.dirname(up) == up: break
        up = os.path.dirname(up)
    return d

def free_port():
    with socket.socket() as s: s.bind(("", 0)); return s.getsockname()[1]

CHECKABLE = (".txt", ".md", ".pdf", ".pptx", ".docx", ".html", ".htm")

def changed_files(since):
    """Changed deliverables in the current git repo: since REF if given, else against HEAD; plus new untracked files."""
    g = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.split("\n")
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    names = g("diff", "--name-only", "--diff-filter=ACMR", since or "HEAD") + g("ls-files", "--others", "--exclude-standard")
    return sorted({os.path.join(top, n) for n in names if n.lower().endswith(CHECKABLE) and os.path.isfile(os.path.join(top, n))})

def main(args):
    extra = args[args.index("--") + 1:] if "--" in args else []
    stress = "--no-stress" not in extra; extra = [x for x in extra if x != "--no-stress"]
    items = args[:args.index("--")] if "--" in args else args
    since = items[items.index("--since") + 1] if "--since" in items and items.index("--since") + 1 < len(items) else None
    if "--changed" in items or since:
        items = [x for x in items if x not in ("--changed", "--since", since)] + changed_files(since)
        if not items: print("ADAMS CHECK: CLEAN (no changed documents, pages or text files)"); return 0
    if not items: print(__doc__); return 2
    rc = 0
    for x in items:
        e = os.path.splitext(x)[1].lower()
        if not x.startswith("http") and not os.path.exists(x): print(f"--- MISSING input: {x}"); rc = 1; continue
        if x.startswith("http"): rc |= web(x, extra or ["--crawl", "--max", "10"], stress)
        elif e in (".txt", ".md"): rc |= text_file(x)
        elif e == ".pdf": COVER["files"] += 1; rc |= pdf_checks(x)
        elif e in (".pptx", ".docx"):
            COVER["files"] += 1
            if e == ".pptx": rc |= run("textlint", [PY, M("deliverable-visual-qa", "scripts", "textlint.py"), x])
            pdf, d = office_to_pdf(x)
            if pdf: rc |= pdf_checks(pdf)
            if d: shutil.rmtree(d, ignore_errors=True)
        elif e in (".html", ".htm"):
            d, port = serve_root(x), free_port()
            srv = subprocess.Popen([PY, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try: time.sleep(1); rc |= web(f"http://127.0.0.1:{port}/{os.path.relpath(os.path.abspath(x), d)}", extra, stress)
            finally: srv.terminate()
        else: print(f"--- skip {x}: no Adams check for this type"); 
    if TEXT_SEEN:
        print("NEXT (fresh eyes, required for Arabic, posts and scripts): spawn a separate reviewer agent with the text alone and the prompt in modules/humanize-writing/fresh-eyes-prompt.md; fix what it quotes; if no agent is available, say so in the report.")
    if COVER["hits"]: print("HITS: " + ", ".join(f"{k} {v}" for k, v in sorted(COVER["hits"].items())))
    print("ADAMS CHECK:", ("FLAGGED" if rc else "CLEAN") + coverage()); return 1 if rc else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
