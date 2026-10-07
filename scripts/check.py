#!/usr/bin/env python3
"""Adams check: one command that picks the right checks for each input.
Usage: python3 check.py FILE_OR_URL [...]      exit 1 if any check flags something.
  .txt .md   hzlint (--reply for reply/dm names, --doc if it has # headings, --msa for AR/MSA names or playbooks) + arlint if Arabic
  .pdf       line_balance + title_check
  .pptx      textlint (speaker notes and text), then rendered to PDF and checked like a PDF
  .docx      rendered to PDF with LibreOffice (soffice), then checked like a PDF
  .html      served on a temporary local port, then web_balance at 375/768/1440
  http(s)    web_balance --crawl --max 10 (override with extra flags after --)
Dependencies install themselves on first run (see the scripts)."""
import importlib.util, os, re, shutil, socket, subprocess, sys, tempfile, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = lambda *p: os.path.join(ROOT, "modules", *p)
PY = sys.executable
AR = re.compile("[؀-ۿ]")

def run(label, cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    print(f"--- {label} (exit {r.returncode})\n{out[-1500:]}")
    return r.returncode

TEXT_SEEN = False

def profile_groups():
    spec = importlib.util.spec_from_file_location("hz", M("humanize-writing", "scripts", "hzlint.py"))
    hz = importlib.util.module_from_spec(spec); spec.loader.exec_module(hz)
    return hz.load_profile()[1]

def text_file(f):
    global TEXT_SEEN
    TEXT_SEEN = True
    t = open(f, encoding="utf-8", errors="ignore").read(); n = os.path.basename(f).lower(); flags = []
    if re.search(r"reply|dm|comment", n): flags.append("--reply")
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

def web(url, extra):
    return run("web_balance " + url, ["node", M("line-balance", "scripts", "web_balance.js"), "--base", url, *extra])

def free_port():
    with socket.socket() as s: s.bind(("", 0)); return s.getsockname()[1]

def main(args):
    extra = args[args.index("--") + 1:] if "--" in args else []
    items = args[:args.index("--")] if "--" in args else args
    if not items: print(__doc__); return 2
    rc = 0
    for x in items:
        e = os.path.splitext(x)[1].lower()
        if not x.startswith("http") and not os.path.exists(x): print(f"--- MISSING input: {x}"); rc = 1; continue
        if x.startswith("http"): rc |= web(x, extra or ["--crawl", "--max", "10"])
        elif e in (".txt", ".md"): rc |= text_file(x)
        elif e == ".pdf": rc |= pdf_checks(x)
        elif e in (".pptx", ".docx"):
            if e == ".pptx": rc |= run("textlint", [PY, M("deliverable-visual-qa", "scripts", "textlint.py"), x])
            pdf, d = office_to_pdf(x)
            if pdf: rc |= pdf_checks(pdf)
            if d: shutil.rmtree(d, ignore_errors=True)
        elif e in (".html", ".htm"):
            d, port = os.path.dirname(os.path.abspath(x)), free_port()
            srv = subprocess.Popen([PY, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try: time.sleep(1); rc |= web(f"http://127.0.0.1:{port}/{os.path.basename(x)}", extra)
            finally: srv.terminate()
        else: print(f"--- skip {x}: no Adams check for this type"); 
    if TEXT_SEEN:
        print("NEXT (fresh eyes, required for Arabic, posts and scripts): spawn a separate reviewer agent with the text alone and the prompt in modules/humanize-writing/fresh-eyes-prompt.md; fix what it quotes; if no agent is available, say so in the report.")
    print("ADAMS CHECK:", "FLAGGED" if rc else "CLEAN"); return 1 if rc else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
