#!/usr/bin/env python3
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import common as c
HERE = os.path.dirname(os.path.abspath(__file__))
repo, _, ev = c.args()

import socket, subprocess, time

_out = []

def scan():
    """web_balance --stress on index.html at 375 and 1440, served from a temporary local port. Cached."""
    if _out: return _out[0]
    with socket.socket() as so: so.bind(("", 0)); port = so.getsockname()[1]
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=repo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1)
        r = subprocess.run(["node", os.path.join(c.ROOT, "modules", "line-balance", "scripts", "web_balance.js"), "--base", f"http://127.0.0.1:{port}/index.html", "--widths", "375,1440", "--stress"], capture_output=True, text=True, timeout=300)
    finally: srv.terminate()
    _out.append(r)
    return r

def need_browser():
    r = scan()
    if r.returncode == 2: return "skip", "Playwright or Chromium is missing: " + (r.stderr or r.stdout).strip()[:120]
    return True, ""

def no_stress():
    r = scan()
    hits = [l for l in r.stdout.splitlines() if l.startswith("STRESS")]
    return not hits, f"{len(hits)} STRESS hits, first: {hits[0][:160]}" if hits else ""

def no_orphans():
    r = scan()
    hits = [l for l in r.stdout.splitlines() if re.match(r"(ORPHAN|WRAPPED|HERO|UNEVEN|GRID|EDGE|CROP|NEST|SLANT|SHRUNK)\b", l) and "plan" in l]
    return not hits, "balance hits on the plan elements: " + (hits[0][:160] if hits else "")

def content():
    html = " ".join(c.read(repo, "index.html").split())
    names = all(re.search(rf"<h2[^>]*>\s*{n}\s*</h2>", html) for n in ("Starter", "Team", "Business"))
    return names and html.count("per month") >= 3 and "Every plan includes email support." in html, "plan names, prices or the note are missing"

sys.exit(c.main([
    (0.0, "browser available", need_browser),
    (0.5, "web_balance --stress reports no STRESS hit", no_stress),
    (0.25, "no ORPHAN, WRAPPED or other balance hit on the plan elements", no_orphans),
    (0.25, "all plan names, prices and the note are still there", content),
]))
