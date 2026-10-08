#!/usr/bin/env python3
"""AI-search readiness audit (GEO/AEO). Usage: python3 ai_search_audit.py URL_OR_FOLDER
URL: fetches only that site's own pages (home, /robots.txt, /llms.txt, /sitemap.xml, up to 5 same-site links), 10 s timeout, never follows a redirect to another host.
Folder: reads the local .html files (and robots.txt, llms.txt, sitemap.xml in its root). Prints PASS / WARN / NOTE / FAIL lines.
Exit 1 when any FAIL (broken JSON-LD, robots blocking everyone, missing title), else 0."""
import json, os, re, sys, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser
from urllib.robotparser import RobotFileParser

BOTS = ["GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended", "OAI-SearchBot"]
SKIP_EXT = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".css", ".js", ".xml", ".zip", ".ico", ".mp4", ".txt", ".json")
Q_START = re.compile(r"^(how|what|why|when|who|which|where|can|does|do|is|are|should|will)\b", re.I)
ORG_TYPES = {"Organization", "Corporation", "LocalBusiness", "WebSite"}
out = []

def say(level, msg): out.append(level); print(f"{level:<5} {msg}")

class Page(HTMLParser):
    def __init__(s):
        super().__init__(); s.title = s.desc = s.canon = s.site = None; s.h1 = 0; s.heads = []; s.links = []; s.ld = []; s._cap = None; s._buf = []
    def handle_starttag(s, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "meta":
            if a.get("name", "").lower() == "description": s.desc = a.get("content", "").strip()
            if a.get("property", "").lower() == "og:site_name": s.site = a.get("content", "").strip()
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split(): s.canon = a.get("href", "")
        elif tag == "a" and a.get("href"): s.links.append(a["href"])
        elif tag in ("title", "h1", "h2", "h3") or (tag == "script" and "ld+json" in a.get("type", "").lower()):
            s._cap, s._buf = tag, []
            if tag == "h1": s.h1 += 1
    def handle_data(s, d):
        if s._cap: s._buf.append(d)
    def handle_endtag(s, tag):
        if tag != s._cap: return
        t = " ".join("".join(s._buf).split())
        if tag == "title" and s.title is None: s.title = t
        elif tag in ("h2", "h3"): s.heads.append(t)
        elif tag == "script": s.ld.append("".join(s._buf))
        s._cap = None

class SameHost(urllib.request.HTTPRedirectHandler):
    def redirect_request(s, req, fp, code, msg, headers, newurl):
        host = lambda u: (urllib.parse.urlparse(u).hostname or "").removeprefix("www.")
        return super().redirect_request(req, fp, code, msg, headers, newurl) if host(newurl) == host(req.full_url) else None

def fetch(url):
    try:
        r = urllib.request.build_opener(SameHost).open(urllib.request.Request(url, headers={"User-Agent": "adams-ai-search-audit"}), timeout=10)
        return r.read(2_000_000).decode("utf-8", "replace") if r.status == 200 else None
    except (urllib.error.URLError, OSError, ValueError): return None

def types_of(node):
    """Yield (type, name) for every typed object in a JSON-LD value, including @graph and nesting."""
    if isinstance(node, list):
        for n in node: yield from types_of(n)
    elif isinstance(node, dict):
        t = node.get("@type"); name = node.get("name") if isinstance(node.get("name"), str) else None
        for x in (t if isinstance(t, list) else [t] if t else []): yield x, name
        for v in node.values():
            if isinstance(v, (list, dict)): yield from types_of(v)

def load(target):
    """Return (pages {label: html}, robots, llms, sitemap_present)."""
    if os.path.isdir(target):
        rd = lambda n: open(os.path.join(target, n), encoding="utf-8", errors="replace").read() if os.path.isfile(os.path.join(target, n)) else None
        pages = {}
        for root, _, files in os.walk(target):
            for f in sorted(files):
                if f.lower().endswith((".html", ".htm")):
                    p = os.path.join(root, f); pages[os.path.relpath(p, target)] = open(p, encoding="utf-8", errors="replace").read()
        return dict(sorted(pages.items())[:50]), rd("robots.txt"), rd("llms.txt"), rd("sitemap.xml") is not None
    base = target if "//" in target else "https://" + target
    u = urllib.parse.urlparse(base); root = f"{u.scheme}://{u.netloc}"
    home = fetch(base); pages = {"/": home} if home else {}
    if home:
        p = Page(); p.feed(home); seen = {"/"}
        for h in p.links:
            x = urllib.parse.urlparse(urllib.parse.urljoin(base, h.split("#")[0]))
            path = x.path or "/"
            if x.hostname and x.hostname.removeprefix("www.") == (u.hostname or "").removeprefix("www.") and path not in seen and not path.lower().endswith(SKIP_EXT) and len(seen) < 6:
                seen.add(path); html = fetch(f"{root}{path}")
                if html: pages[path] = html
    robots = fetch(root + "/robots.txt")
    return pages, robots, fetch(root + "/llms.txt"), bool(fetch(root + "/sitemap.xml")) or bool(robots and re.search(r"(?im)^sitemap:", robots))

def audit(target):
    pages, robots, llms, sitemap = load(target)
    if not pages: say("FAIL", f"no pages found at {target}"); return
    say("PASS" if llms else "WARN", "llms.txt exists" if llms else "llms.txt missing (optional file; no major AI search provider has confirmed it reads it, see references/ai-search.md)")
    if robots is None: say("WARN", "robots.txt missing (AI crawlers are then allowed by default)")
    else:
        rp = RobotFileParser(); rp.parse(robots.splitlines())
        if not rp.can_fetch("*", "/"): say("FAIL", "robots.txt blocks all crawlers (User-agent: * with Disallow: /)")
        blocked = [b for b in BOTS if not rp.can_fetch(b, "/")]
        say("WARN" if blocked else "PASS", f"robots.txt blocks AI bots: {', '.join(blocked)} (confirm this is intended)" if blocked else "robots.txt does not block GPTBot, ClaudeBot, PerplexityBot, Google-Extended, OAI-SearchBot")
    say("PASS" if sitemap else "WARN", "sitemap present" if sitemap else "sitemap.xml missing")
    spell = {}  # normalized brand -> {raw spelling: where}
    note = lambda raw, where: spell.setdefault(re.sub(r"[^a-z0-9]", "", raw.lower()), {}).setdefault(raw, where) if raw else None
    parsed = {}
    for label, html in pages.items():
        p = Page(); p.feed(html); parsed[label] = p; note(p.site, f"{label} og:site_name")
        is_home = label in ("/", "index.html")
        types = set()
        for raw in p.ld:
            try: data = json.loads(raw)
            except ValueError: say("FAIL", f"{label}: broken JSON-LD (does not parse)"); continue
            for t, name in types_of(data):
                types.add(t)
                if t in ORG_TYPES: note(name, f"{label} JSON-LD {t}")
        say("PASS" if p.ld and types else "WARN", f"{label}: JSON-LD valid, types {', '.join(sorted(types))}" if types else f"{label}: no valid JSON-LD")
        if not p.title: say("FAIL", f"{label}: missing title")
        else: say("PASS" if 10 <= len(p.title) <= 70 else "WARN", f"{label}: title {len(p.title)} chars (want 10-70)")
        d = len(p.desc or ""); say("PASS" if 50 <= d <= 170 else "WARN", f"{label}: meta description {d} chars (want 50-170)")
        say("PASS" if p.canon else "WARN", f"{label}: canonical " + ("set" if p.canon else "missing"))
        say("PASS" if p.h1 == 1 else "WARN", f"{label}: {p.h1} h1 (want exactly 1)")
        if is_home and not types & ORG_TYPES: say("WARN", f"{label}: add Organization JSON-LD on the home page")
        low = label.lower()
        want = ("Article", "BlogPosting", "NewsArticle") if re.search(r"blog|post|article|news", low) else ("Product", "Offer") if re.search(r"product|pricing|plans|shop", low) else ()
        if want and not types & set(want): say("WARN", f"{label}: consider {' or '.join(want[:2])} JSON-LD for this page type")
        qs = [h for h in p.heads if h.endswith("?") or Q_START.match(h)]
        if qs and "FAQPage" not in types: say("NOTE", f"{label}: {len(qs)} question heading(s); if the answers are on the page, FAQPage schema can mirror them")
    for p_label, p in parsed.items():  # a title segment that matches a known brand must be spelled the same way
        for seg in re.split(r"\s[|·:-]\s", p.title or ""):
            if re.sub(r"[^a-z0-9]", "", seg.lower()) in spell: note(seg.strip(), f"{p_label} title")
    bad = {k: v for k, v in spell.items() if len(v) > 1}
    for v in bad.values(): say("WARN", "brand name spelled differently: " + "; ".join(f'"{r}" in {w}' for r, w in v.items()))
    if spell and not bad: say("PASS", "brand name spelled the same in JSON-LD, title and og:site_name")

def main(args):
    if len(args) != 1: print(__doc__); return 2
    audit(args[0])
    print(f"AI SEARCH AUDIT: {out.count('FAIL')} FAIL, {out.count('WARN')} WARN, {out.count('PASS')} PASS")
    return 1 if "FAIL" in out else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
