#!/usr/bin/env node
// Line balance check for live web pages (sites, SaaS dashboards, academies), English and Arabic.
//
// Usage:
//   node web_balance.js --base https://site.com [--urls urls.txt] [--crawl] [--max 300]
//        [--widths 375,768,1440] [--auth role=state.json ...] [--min 0.3] [--stress|--stress-all] [--out report.json]
//   node web_balance.js login --url https://site.com/login --out admin.json
//        (reads LB_EMAIL and LB_PASSWORD from env; optional LB_EMAIL_SEL, LB_PASS_SEL, LB_SUBMIT_SEL)
//
// urls.txt: one path or URL per line. Add page states after "|":
//   /pricing
//   /dashboard | click:[data-test=open-modal] | wait:500
//   @admin /admin/users            (the @role prefix uses that --auth storage state)
// Lines starting with # are ignored.
//
// Flags per text block, at every width:
//   ORPHAN   last line is one word, or shorter than --min of the widest line
//   WRAPPED  a short item (bullet, button, label, chip, nav link, table header, h2-h6) runs onto 2+ lines
//   HERO     an h1 longer than 2 lines
//   UNEVEN   3+ sibling blocks in one row (same top, tag, class, size) with different line counts
//   GRID     a CSS grid whose last row is only partly filled (5 items in 3 columns, a lone card)
//   EDGE     table content closer than 12px to the border or fill edge of the box that holds the table
//   CROP     a decorative round shape cut off by a clipping ancestor or the viewport edge
//   NEST     three or more framed boxes (240x120 or larger) inside one another
//   SLANT    a large painted band cut by a diagonal clip-path or skewed (shapes stay closed)
//   STRESS   (--stress) layout breakage after mutating a copy of the live DOM, at 375 and 1440 only: kinds long-text (twice the words),
//            long-token (a 40 character unbroken string), big-numbers (9-digit values), empty (list and table text blanked).
//            Reasons: page-overflow, past-parent, past-own-box, clipped, overlap. Breakage already there before any mutation prints once
//            as kind as-is. Skipped above 20 pages unless --stress-all. The page is reloaded between kinds.
//   DIAGRAM  in a container with 3+ absolutely positioned text nodes or a large inline SVG: text, positioned boxes and SVG shapes within 8px, overlapping or outside the container
//   MARKER   3+ repeated rows with a small marker: marker centres off one x (1px), off the first text line (2px), or a connector off the centres
//   SHRUNK   a script changed an element's inline font-size after load (type shrunk to fit; fix the copy or the CSS)
//   Page checks (page_checks.js, plus the Tab, link and console parts below), at every width:
//   PLACEHOLDER lorem ipsum, TODO, FIXME, TBD, {{ }}, undefined, NaN, null, [object Object] or ${ in visible text (code, pre, kbd, samp and aria-hidden are ignored)
//   COUNT    a heading stating a count ("Six principles", "3 steps") above a list or grid with another number of items
//   GAP      stacked sections closer than 12px or overlapping; GAP-RHYTHM: more than two different gaps between sections (first and last excluded)
//   TABLE    number columns not right aligned or without tabular-nums, text columns not left aligned, header off its column, content under 16px from the frame
//   SUBLINE  a paragraph after an h1 to h3 that does not share its start edge (or centre), or is wider than a width-limited heading
//   THIN     (1280px and wider) main content under 55% of the viewport with no sidebar, not a reading page
//   A11Y     contrast under 4.5:1 (3:1 for large text), touch targets under 44x44 (480px and narrower), img without alt, heading level skip, no visible focus style on Tab
//   BROKEN   same-site links answering 404 (HEAD then GET, at most 200 per run; file:// targets must exist), images that did not load, console errors, uncaught page errors
//   COPY     U+2014 or U+2013 in visible text, exclamation marks in headings, buttons and labels, Title Case headings
//   COVER    a fixed or sticky element covering text or controls at scroll 0, a role=dialog without aria-modal, an anchor target hidden under a sticky header
//   RTL      under dir=rtl: direction arrows not mirrored, text-align: left or float: left on RTL text
// Exit code 1 when anything is flagged. FLAGGED counts unique defects; ROUTE-HITS is the raw count over every page and width.
// Hash routes (#/x, #!/x, [data-route]) of one document are loaded once and switched per width. A WARNING line is printed
// when in-page routes were not scanned (no --crawl or --urls) or the crawl hit --max.
//
// Self-installing: if Playwright or its Chromium is missing, the script installs them once
// into ~/.cache/adams-line-balance (outside every project, so no package.json is touched).
// Free and local; about 10 MB for the package and about 150 MB for Chromium, shared by all projects.

const fs = require("fs");
const os = require("os");
const path = require("path");
const { execSync } = require("child_process");

const CACHE = process.env.LB_CACHE || path.join(os.homedir(), ".cache", "adams-line-balance");

function loadPlaywright() {
  for (const from of [process.cwd(), CACHE]) {
    try { return require(require.resolve("playwright", { paths: [from] })); } catch {}
  }
  if (process.env.ADAMS_AUTO_INSTALL === "0") { console.error("Playwright is missing and auto-install is off (ADAMS_AUTO_INSTALL=0). Install it: npm install playwright@1.63.0"); process.exit(2); }
  console.log(`[setup] Playwright not found, installing it once into ${CACHE} ...`);
  fs.mkdirSync(CACHE, { recursive: true });
  if (!fs.existsSync(path.join(CACHE, "package.json"))) fs.writeFileSync(path.join(CACHE, "package.json"), '{"name":"adams-line-balance-cache","private":true}');
  execSync("npm install --no-audit --no-fund --silent playwright@1.63.0", { cwd: CACHE, stdio: "inherit" });
  return require(require.resolve("playwright", { paths: [CACHE] }));
}

const pw = loadPlaywright();
const { inspectPage } = require("./page_checks.js");

async function launch() {
  try { return await pw.chromium.launch(); } catch (e) {
    if (!/Executable doesn't exist|browserType.launch|install/i.test(e.message)) throw e;
    if (process.env.ADAMS_AUTO_INSTALL === "0") { console.error("Chromium is missing and auto-install is off (ADAMS_AUTO_INSTALL=0). Run: npx playwright install chromium"); process.exit(2); }
    console.log("[setup] Chromium not found, downloading it once ...");
    const cli = path.join(path.dirname(require.resolve("playwright/package.json", { paths: [process.cwd(), CACHE] })), "cli.js");
    execSync(`"${process.execPath}" "${cli}" install chromium`, { stdio: "inherit" });
    return await pw.chromium.launch();
  }
}

const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf("--" + k); return i >= 0 ? argv[i + 1] : d; };
const many = (k) => argv.flatMap((a, i) => (a === "--" + k ? [argv[i + 1]] : []));
const has = (k) => argv.includes("--" + k);

async function login() {
  const url = opt("url"), out = opt("out", "state.json");
  const { LB_EMAIL, LB_PASSWORD } = process.env;
  if (!url || !LB_EMAIL || !LB_PASSWORD) throw new Error("login needs --url and LB_EMAIL / LB_PASSWORD in env");
  const b = await launch();
  const ctx = await b.newContext();
  const p = await ctx.newPage();
  await p.goto(url, { waitUntil: "networkidle" });
  await p.fill(process.env.LB_EMAIL_SEL || 'input[type=email], input[name=email]', LB_EMAIL);
  await p.fill(process.env.LB_PASS_SEL || 'input[type=password]', LB_PASSWORD);
  await Promise.all([p.waitForLoadState("networkidle"), p.click(process.env.LB_SUBMIT_SEL || 'button[type=submit]')]);
  await p.waitForTimeout(1500);
  if (p.url() === url) console.warn("warning: still on the login URL, check the selectors or credentials");
  await ctx.storageState({ path: out });
  await b.close();
  console.log("saved session to", out, "(keep it out of git)");
}

// Runs inside the page. Returns the defects for the current viewport.
function inspect(MIN) {
  const SHORT = new Set(["LI", "BUTTON", "LABEL", "TH", "A", "SUMMARY", "OPTION", "LEGEND", "FIGCAPTION", "DT", "H2", "H3", "H4", "H5", "H6"]);
  const BLOCK_SKIP = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "CODE", "PRE", "KBD", "SAMP", "TEXTAREA", "INPUT", "SELECT", "SVG", "MATH"]);
  const bcache = new WeakMap();
  const isBlockish = (el) => {
    if (!bcache.has(el)) { const d = getComputedStyle(el).display; bcache.set(el, d !== "inline" && d !== "contents"); }
    return bcache.get(el);
  };
  const visible = (el) => {
    const s = getComputedStyle(el);
    if (s.visibility === "hidden" || s.display === "none" || +s.opacity === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  // A text block = a block-level element that owns text directly or through inline children only.
  const blocks = [];
  const walk = (el) => {
    if (BLOCK_SKIP.has(el.tagName) || el.closest("[aria-hidden=true],[data-lb-ignore]")) return;
    // display:contents has no box of its own (a wrapper like `md:contents`), so it looks invisible; look through it.
    // Without this the whole page under such a wrapper was skipped and only narrow widths were checked.
    if (getComputedStyle(el).display === "contents") { [...el.children].forEach(walk); return; }
    if (!visible(el)) return;
    const kids = [...el.children];
    const ownText = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    // Any block-level descendant (not only direct children) means this is a container, not a text block:
    // wrappers with display:contents or inline would otherwise hide a whole section inside one "paragraph".
    const blockKids = [...el.querySelectorAll("*")].filter((d) => !BLOCK_SKIP.has(d.tagName.toUpperCase()) && isBlockish(d) && visible(d));
    if (ownText && blockKids.length === 0 && isBlockish(el)) { blocks.push(el); return; }
    // Own text beside block children (a flex node holding a numeral and a bare label): measure the own text, then keep walking.
    // Before, this text was in no block at all and a wrapping label there was never seen.
    if (ownText && isBlockish(el)) blocks.push(el);
    if (!ownText && blockKids.length === 0 && kids.length && isBlockish(el) && (el.innerText || "").trim()) { blocks.push(el); return; }
    kids.forEach(walk);
  };
  walk(document.body);

  const out = [];
  const meta = [];
  const tbox = new WeakMap(); // text block -> glyph box, for DIAGRAM
  // A short phrase that sits in a diagram node: inside an absolutely positioned box (up to two levels up), or a flex row item
  // (or the own text of a flex row). Up to 12 words with no sentence punctuation (a trailing . ! ? makes it a sentence). Never a P or H1.
  const nodeOf = (el, words, text) => {
    if (el.tagName === "P" || el.tagName === "H1" || words.length > 12 || /[.!?;:]\s+\S|[.!?]$/.test(text)) return null;
    for (let a = el, i = 0; a && a !== document.body && i < 3; a = a.parentElement, i++) if (getComputedStyle(a).position === "absolute") return a;
    const row = (x) => x && /flex/.test(getComputedStyle(x).display) && !/column/.test(getComputedStyle(x).flexDirection);
    return row(el.parentElement) || row(el) ? el : null;
  };
  const groups = new Map(); // diagram siblings: container + class -> node -> lines
  for (const el of blocks) {
    // Collect one rect per word (works for LTR and RTL, since we only use geometry).
    const words = [];
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = tw.nextNode())) {
      if (n.parentElement.closest("code,pre,svg,[aria-hidden=true]")) continue;
      let o = n.parentElement; while (o !== el && !isBlockish(o)) o = o.parentElement;
      if (o !== el) continue; // belongs to a block child, measured on its own
      const re = /\S+/g; let m;
      while ((m = re.exec(n.textContent))) {
        const r = document.createRange(); r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length);
        const rects = [...r.getClientRects()].filter((q) => q.width > 0);
        if (rects.length) words.push({ t: m[0], top: rects[0].top, l: Math.min(...rects.map((q) => q.left)), r: Math.max(...rects.map((q) => q.right)), h: rects[0].height });
      }
    }
    // An inline-block chip (a code span) sits in the line like a word: without its box a line that ends in a chip reads as a stub.
    for (const c of el.querySelectorAll("*")) {
      if (!/^inline-(block|flex|grid)$/.test(getComputedStyle(c).display) || c.parentElement.closest("code,pre,svg,[aria-hidden=true]")) continue;
      let o = c.parentElement; while (o !== el && !isBlockish(o)) o = o.parentElement;
      const q = c.getBoundingClientRect(), b = el.getBoundingClientRect();
      if (o === el && q.width > 0) for (let i = 0, k = (c.textContent.match(/\S+/g) || []).length || 1; i < k; i++) words.push({ t: "\u25a1", top: q.top, l: q.left, r: Math.min(q.right, b.right), h: q.height });
    }
    if (!words.length) continue;
    const lines = [];
    for (const w of words) {
      const L = lines.find((x) => Math.abs(x.top - w.top) < w.h * 0.5);
      if (L) { L.l = Math.min(L.l, w.l); L.r = Math.max(L.r, w.r); L.words.push(w.t); }
      else lines.push({ top: w.top, l: w.l, r: w.r, words: [w.t] });
    }
    lines.sort((a, b) => a.top - b.top);
    // Own text only when block children carry the rest (a numeral next to a bare label).
    const mixedKids = [...el.children].some((k) => isBlockish(k) && visible(k));
    const text = (mixedKids ? words.map((x) => x.t).join(" ") : (el.innerText || "")).replace(/\s+/g, " ").trim().slice(0, 70);
    const tag = el.tagName;
    const cs = getComputedStyle(el);
    tbox.set(el, { l: Math.min(...words.map((x) => x.l)), r: Math.max(...words.map((x) => x.r)), t: Math.min(...words.map((x) => x.top)), b: Math.max(...words.map((x) => x.top + x.h)) });
    const sel = tag.toLowerCase() + (el.id ? "#" + el.id : "") + (el.classList.length ? "." + [...el.classList].slice(0, 2).join(".") : "");
    const rect = el.getBoundingClientRect();
    meta.push({ key: `${Math.round(rect.top / 3)}|${tag}|${el.className}|${cs.fontSize}`, n: lines.length, text, sel });
    const node = nodeOf(el, words, text);
    if (node) {
      // Sibling nodes of one diagram: the node itself, and the row that holds a numeral plus label.
      for (const m of node === el ? [el, el.parentElement] : [node]) {
        if (!m || !m.parentElement) continue;
        const k = m.parentElement.tagName + "|" + (typeof m.className === "string" ? m.className : "") + "|" + cs.fontSize;
        const g = groups.get(k) || groups.set(k, new Map()).get(k);
        const p = g.get(m);
        g.set(m, { n: Math.max(lines.length, p ? p.n : 0), text: p ? p.text : text, sel: p ? p.sel : sel });
      }
    }
    if (lines.length < 2) continue;
    // Short text is told by tag, role and rendering, never by class name. A paragraph (P) or text over 8 words is never short.
    const chipLike = () => {
      if (words.length > 6 || text.length > 40) return false;
      let a = el;
      for (let i = 0; a && i < 3; i++, a = a.parentElement) {
        const s = getComputedStyle(a);
        if (/^inline-(block|flex|grid)$/.test(s.display)) return true;
        const r = a.getBoundingClientRect(), rad = parseFloat(s.borderTopLeftRadius) * (/%/.test(s.borderTopLeftRadius) ? r.height / 100 : 1);
        if ((s.backgroundColor !== "rgba(0, 0, 0, 0)" || parseFloat(s.borderTopWidth) > 0) && rad >= r.height / 2) return true;
      }
      return false;
    };
    const isShort = tag !== "P" && (SHORT.has(tag) || el.closest("li,button,label,th,nav,[role=tab],[role=button]") || chipLike());
    if (tag === "H1") { if (lines.length > 2) out.push({ type: "HERO", lines: lines.length, text, sel }); continue; }
    if (node || (isShort && words.length <= 8)) { out.push({ type: "WRAPPED", lines: lines.length, text, sel }); continue; }
    const widest = Math.max(...lines.slice(0, -1).map((x) => x.r - x.l));
    const last = lines[lines.length - 1];
    const ratio = (last.r - last.l) / widest;
    if (last.words.length === 1 || ratio < MIN)
      out.push({ type: "ORPHAN", lines: lines.length, last: Math.round(ratio * 100) + "%", tail: last.words.join(" "), text, sel });
  }
  const rows = {};
  for (const m of meta) (rows[m.key] = rows[m.key] || []).push(m);
  for (const k in rows) {
    const r = rows[k];
    if (r.length >= 3 && new Set(r.map((x) => x.n)).size > 1)
      out.push({ type: "UNEVEN", counts: r.map((x) => x.n), text: r.map((x) => x.text.slice(0, 20)).join(" | "), sel: r[0].sel });
  }
  for (const g of groups.values()) {
    const r = [...g.values()];
    if (r.length >= 3 && new Set(r.map((x) => x.n)).size > 1)
      out.push({ type: "UNEVEN", counts: r.map((x) => x.n), text: r.map((x) => x.text.slice(0, 20)).join(" | "), sel: r[0].sel });
  }
  // GRID: a CSS grid whose last row is only partly filled (5 items in 3 columns,
  // a lone card). Compares occupied width, so spanning cells count correctly.
  for (const g of document.querySelectorAll("*")) {
    if (getComputedStyle(g).display !== "grid") continue;
    const kids = [...g.children].filter((c) => { const s = getComputedStyle(c); return s.display !== "none" && s.position !== "absolute" && s.position !== "fixed" && c.getBoundingClientRect().width > 0 && c.getBoundingClientRect().height > 0; });
    if (kids.length < 2) continue;
    // One grid row = cells whose vertical extents overlap (align-items:center puts a short cell's top below its row's top).
    const byRow = {};
    let cur = null;
    for (const r of kids.map((c) => c.getBoundingClientRect()).sort((a, b) => a.top - b.top)) {
      if (!cur || r.top >= cur.bottom - 1) { cur = { top: Math.round(r.top), bottom: r.bottom }; byRow[cur.top] = []; }
      cur.bottom = Math.max(cur.bottom, r.bottom);
      byRow[cur.top].push(r);
    }
    const tops = Object.keys(byRow).map(Number).sort((a, b) => a - b);
    if (tops.length < 2 || byRow[tops[0]].length < 2) continue;
    const span = (rs) => Math.max(...rs.map((r) => r.right)) - Math.min(...rs.map((r) => r.left));
    const first = byRow[tops[0]], last = byRow[tops[tops.length - 1]];
    if (span(last) < span(first) * 0.9)
      out.push({ type: "GRID", counts: tops.map((t) => byRow[t].length), text: (g.innerText || "").trim().slice(0, 60), sel: g.tagName.toLowerCase() + (g.className && typeof g.className === "string" ? "." + g.className.trim().split(/\s+/).join(".") : "") });
  }
  // EDGE: table content closer than 12px to the visible edge (border or fill) of the
  // box that holds the table. Checkboxes or figures touching the frame read as broken.
  const framed = (el) => { const s = getComputedStyle(el); return parseFloat(s.borderLeftWidth) > 0 || parseFloat(s.borderRightWidth) > 0 || (s.backgroundColor !== "rgba(0, 0, 0, 0)" && s.backgroundColor !== "transparent"); };
  for (const t of document.querySelectorAll("table")) {
    if (!t.getBoundingClientRect().width) continue;
    let frame = t;
    while (frame && frame !== document.body && !framed(frame)) frame = frame.parentElement;
    if (!frame || frame === document.body) continue;
    const fr = frame.getBoundingClientRect(), fs = getComputedStyle(frame);
    const left = fr.left + parseFloat(fs.borderLeftWidth), right = fr.right - parseFloat(fs.borderRightWidth);
    // A table wider than its box scrolls inside it: measure the left gap at the start of the scroll and the right gap at the end.
    const scroller = (() => { for (let a = t.parentElement; a && a !== document.body; a = a.parentElement) { const st = getComputedStyle(a); if (/(auto|scroll)/.test(st.overflowX) && a.scrollWidth > a.clientWidth + 1) return a; } return null; })();
    const gapFor = (side) => {
      let w = Infinity;
      for (const row of t.rows) {
        // A header kept for screen readers only (clipped to a 1px box) is not visible, so it has no edge to touch.
        const sec = row.parentElement;
        if (sec && sec.tagName === "THEAD" && (getComputedStyle(sec).clipPath !== "none" || sec.getBoundingClientRect().width <= 2)) continue;
        const cells = [...row.cells].filter((c) => c.getBoundingClientRect().width);
        if (!cells.length) continue;
        const c = side === "l" ? cells[0] : cells[cells.length - 1];
        const kids = [...c.querySelectorAll("*")].filter((k) => k.getBoundingClientRect().width && !k.children.length);
        const rects = kids.length ? kids.map((k) => k.getBoundingClientRect()) : [];
        if (!rects.length) { const rg = document.createRange(); rg.selectNodeContents(c); const r = rg.getBoundingClientRect(); if (r.width) rects.push(r); }
        for (const r of rects) w = Math.min(w, side === "l" ? r.left - left : right - r.right);
      }
      return w;
    };
    let worst = gapFor("l");
    if (scroller) { const keep = scroller.scrollLeft; scroller.scrollLeft = scroller.scrollWidth; worst = Math.min(worst, gapFor("r")); scroller.scrollLeft = keep; }
    else worst = Math.min(worst, gapFor("r"));
    if (worst < 12)
      out.push({ type: "EDGE", gap: Math.round(worst) + "px", text: (t.innerText || "").trim().slice(0, 50), sel: "table" + (t.className && typeof t.className === "string" ? "." + t.className.trim().split(/\s+/).join(".") : "") });
  }
  // CROP: a decorative shape (no text, round or large) cut off by a clipping
  // ancestor or the viewport edge. Reads as a rendering bug, not a design.
  const clipper = (el) => { for (let a = el.parentElement; a && a !== document.documentElement; a = a.parentElement) { const s = getComputedStyle(a); if (/(hidden|clip)/.test(s.overflow + s.overflowX + s.overflowY)) return a; } return null; };
  for (const el of document.querySelectorAll("body *")) {
    if ((el.innerText || "").trim() || el.querySelector("img,svg,canvas,video,input,button")) continue;
    const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    if (r.width < 40 || r.height < 40 || s.visibility === "hidden" || s.opacity === "0") continue;
    const round = parseFloat(s.borderTopLeftRadius) >= Math.min(r.width, r.height) / 2 - 1 || /%/.test(s.borderTopLeftRadius) && parseFloat(s.borderTopLeftRadius) >= 50;
    const painted = s.backgroundColor !== "rgba(0, 0, 0, 0)" || s.backgroundImage !== "none";
    if (!round || !painted) continue;
    const c = clipper(el), box = c ? c.getBoundingClientRect() : { left: 0, top: -Infinity, right: innerWidth, bottom: Infinity };
    const cut = Math.max(box.left - r.left, box.top - r.top, r.right - box.right, r.bottom - box.bottom);
    if (cut > 2) out.push({ type: "CROP", cut: Math.round(cut) + "px", text: "", sel: el.tagName.toLowerCase() + (typeof el.className === "string" && el.className.trim() ? "." + el.className.trim().split(/\s+/).join(".") : "") });
  }
  // SLANT: a large painted band cut by a diagonal clip-path or skewed: the owner
  // wants every shape closed and complete (7 Oct 2026).
  for (const el of document.querySelectorAll("body *")) {
    const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    if (r.width < 300 || r.height < 80) continue;
    const painted = s.backgroundColor !== "rgba(0, 0, 0, 0)" || s.backgroundImage !== "none";
    const poly = /polygon\(/.test(s.clipPath) && /polygon\(([^)]*)\)/.exec(s.clipPath)[1].split(",").length >= 3 && !/^polygon\(0(px|%)? 0(px|%)?, 100% 0(px|%)?, 100% 100%, 0(px|%)? 100%\)$/.test(s.clipPath);
    const m = s.transform.match(/^matrix\(([^)]+)\)/), skew = m && Math.abs(parseFloat(m[1].split(",")[2])) > 0.02;
    if (painted && (poly || skew)) out.push({ type: "SLANT", text: "", sel: el.tagName.toLowerCase() + (typeof el.className === "string" && el.className.trim() ? "." + el.className.trim().split(/\s+/).join(".") : "") });
  }
  // NEST: three or more framed boxes (own border or fill different from the
  // parent's), each at least 240x120, inside one another: box > box > box.
  const bgOf = (el) => { for (let a = el; a; a = a.parentElement) { const b = getComputedStyle(a).backgroundColor; if (b !== "rgba(0, 0, 0, 0)" && b !== "transparent") return b; } return "rgb(255, 255, 255)"; };
  const isFrame = (el) => { const r = el.getBoundingClientRect(); if (r.width < 240 || r.height < 120) return false; const s = getComputedStyle(el); if (parseFloat(s.borderTopWidth) > 0 && s.borderTopStyle !== "none") return true; const b = s.backgroundColor; return b !== "rgba(0, 0, 0, 0)" && b !== "transparent" && el.parentElement && b !== bgOf(el.parentElement); };
  const nested = new Set();
  for (const el of document.querySelectorAll("main *, section *")) {
    if (!isFrame(el)) continue;
    let depth = 1, top = el;
    for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) if (isFrame(a)) { depth++; top = a; }
    if (depth >= 3 && !nested.has(top)) { nested.add(top); out.push({ type: "NEST", depth, text: (el.innerText || "").trim().slice(0, 40), sel: top.tagName.toLowerCase() + (typeof top.className === "string" && top.className.trim() ? "." + top.className.trim().split(/\s+/).join(".") : "") }); }
  }
  // DIAGRAM: a container with 3+ absolutely positioned text nodes, or a large inline SVG. Text boxes, positioned boxes and SVG
  // shapes in it must keep 8px apart (arrow polygons on a card, a card on a label) and stay inside the container's box. A box that
  // holds another (a label in its own card, anything inside its ancestor) is by design; so is the large ring or frame that holds
  // most others (the background track), and shapes of one SVG among themselves (an arrow is a line plus a head).
  // Shortcut: bounding boxes, not outlines; an SVG with over 60 shapes is an illustration and is skipped.
  const selOf = (x) => x.tagName.toLowerCase() + (x.id ? "#" + x.id : "") + (typeof x.className === "string" && x.className.trim() ? "." + x.className.trim().split(/\s+/).slice(0, 2).join(".") : "");
  const labelOf = (x) => ((x.innerText || x.textContent || "").replace(/\s+/g, " ").trim().slice(0, 20)) || selOf(x);
  const shapesOf = (svg) => [...svg.querySelectorAll("path,polygon,polyline,circle,ellipse,line,rect")].filter((e) => !e.closest("defs,marker,clipPath,mask,pattern,symbol") && getComputedStyle(e).display !== "none" && getComputedStyle(e).visibility !== "hidden" && +getComputedStyle(e).opacity > 0);
  const shapeBox = (e) => {
    const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    if (!r.width && !r.height) return null;
    let b = { l: r.left, t: r.top, r: r.right, b: r.bottom };
    const m = e.getScreenCTM && e.getScreenCTM(), k = m ? Math.hypot(m.a, m.b) : 1;
    const sw = s.stroke !== "none" ? (parseFloat(s.strokeWidth) || 0) * k / 2 : 0;
    if (s.fill === "none" && s.stroke === "none") return null;
    b = { l: b.l - sw, t: b.t - sw, r: b.r + sw, b: b.b + sw };
    // An arrowhead drawn by marker-start / marker-end is not in the shape's box: add a square around the end point.
    try {
      for (const [prop, at] of [["markerEnd", 1], ["markerStart", 0]]) {
        const id = /url\(["']?#([^"')]+)/.exec(s[prop] || ""); if (!id || !e.getTotalLength) continue;
        const mk = document.getElementById(id[1]); if (!mk) continue;
        const px = mk.getAttribute("markerUnits") === "userSpaceOnUse" ? 1 : (parseFloat(s.strokeWidth) || 1);
        const half = Math.max(parseFloat(mk.getAttribute("markerWidth")) || 3, parseFloat(mk.getAttribute("markerHeight")) || 3) * px * k / 2;
        const pt = e.getPointAtLength(at * e.getTotalLength()), c = new DOMPoint(pt.x, pt.y).matrixTransform(m);
        b = { l: Math.min(b.l, c.x - half), t: Math.min(b.t, c.y - half), r: Math.max(b.r, c.x + half), b: Math.max(b.b, c.y + half) };
      }
    } catch {}
    return b;
  };
  const absNodes = new Map(); // container -> positioned text-bearing boxes
  for (const e of document.querySelectorAll("body *")) {
    if (e.closest("svg,[aria-hidden=true],[data-lb-ignore]") || getComputedStyle(e).position !== "absolute" || !visible(e) || !(e.innerText || "").trim()) continue;
    const q = e.getBoundingClientRect(); if (q.width <= 2 || q.height <= 2) continue; // visually hidden text (a 1px screen reader box)
    const c = e.offsetParent; if (!c || c === document.body || c === document.documentElement) continue;
    (absNodes.get(c) || absNodes.set(c, []).get(c)).push(e);
  }
  const svgBox = (v) => { const r = v.getBoundingClientRect(); return r.width >= 160 && r.height >= 160 && !v.closest("[aria-hidden=true],[data-lb-ignore]") && visible(v); };
  const bigSvgs = [...document.querySelectorAll("svg")].filter((v) => svgBox(v) && shapesOf(v).length >= 3 && shapesOf(v).length <= 60);
  const dcont = new Set([...absNodes.keys()].filter((c) => absNodes.get(c).length >= 3));
  for (const v of bigSvgs) if (v.parentElement && v.parentElement !== document.body) dcont.add(v.parentElement);
  for (const c of dcont) {
    const cb = c.getBoundingClientRect(), items = [];
    const nodes = (absNodes.get(c) || []).slice(0, 40);
    for (const e of nodes) {
      // A box with no frame (no fill, border or shadow) is only its text; a card is its whole box.
      const r = e.getBoundingClientRect(), st = getComputedStyle(e), ts = blocks.filter((x) => e.contains(x) && tbox.get(x)).map((x) => tbox.get(x));
      const framed = st.backgroundColor !== "rgba(0, 0, 0, 0)" || st.backgroundImage !== "none" || st.boxShadow !== "none" || ["Top", "Right", "Bottom", "Left"].some((k) => parseFloat(st["border" + k + "Width"]) > 0 && st["border" + k + "Style"] !== "none");
      const u = !framed && ts.length ? { l: Math.min(...ts.map((x) => x.l)), t: Math.min(...ts.map((x) => x.t)), r: Math.max(...ts.map((x) => x.r)), b: Math.max(...ts.map((x) => x.b)) } : { l: r.left, t: r.top, r: r.right, b: r.bottom };
      items.push({ k: "box", el: e, ...u, name: labelOf(e) });
    }
    for (const e of blocks) {
      const t = tbox.get(e);
      if (!t || !c.contains(e) || nodes.some((n) => n.contains(e)) || e.closest("svg") || e.getBoundingClientRect().width <= 2 || e.getBoundingClientRect().height <= 2) continue;
      items.push({ k: "text", el: e, l: t.l, t: t.t, r: t.r, b: t.b, name: labelOf(e) });
    }
    for (const v of bigSvgs) if (c.contains(v)) for (const e of shapesOf(v)) { const b = shapeBox(e); if (b) items.push({ k: "shape", el: e, svg: v, ...b, name: selOf(e) + "@" + Math.round(b.l) + "," + Math.round(b.t) }); }
    const alive = items.filter((a) => {
      if (a.k !== "shape" || a.r - a.l < 120 || a.b - a.t < 120) return true;
      const inner = items.filter((o) => o !== a && (o.l + o.r) / 2 >= a.l && (o.l + o.r) / 2 <= a.r && (o.t + o.b) / 2 >= a.t && (o.t + o.b) / 2 <= a.b).length;
      return inner < (items.length - 1) * 0.5;
    });
    const has = (a, b) => a.l <= b.l + 1 && a.r >= b.r - 1 && a.t <= b.t + 1 && a.b >= b.b - 1;
    let hits = 0;
    for (let i = 0; i < alive.length && hits < 10; i++) {
      const a = alive[i];
      if (a.l < cb.left - 2 || a.r > cb.right + 2 || a.t < cb.top - 2 || a.b > cb.bottom + 2) { out.push({ type: "DIAGRAM", reason: "outside", text: a.name, sel: selOf(c) }); hits++; }
      for (let j = i + 1; j < alive.length && hits < 10; j++) {
        const o = alive[j];
        if (a.svg && a.svg === o.svg) continue;
        if (a.el.contains(o.el) || o.el.contains(a.el) || has(a, o) || has(o, a)) continue;
        const gap = Math.hypot(Math.max(a.l - o.r, o.l - a.r, 0), Math.max(a.t - o.b, o.t - a.b, 0));
        if (gap < 8) { out.push({ type: "DIAGRAM", reason: gap <= 0 ? "overlap" : "gap " + Math.round(gap) + "px", text: a.name + " | " + o.name, sel: selOf(c) }); hits++; }
      }
    }
  }
  // MARKER: 3+ sibling rows that each hold a small marker (an element up to 20px, or a round numeral badge) next to their text.
  // All marker centres share one x (1px); each sits on the centre of its row's first text line (2px). A connector line (a
  // ::before or ::after of the list or a row, or a thin element up to 3px wide) must run through the marker centres (1px), and a list-level
  // one must start and end on the first and last marker centre (2px). Shortcut: pseudo-element markers and borders are not read.
  // First word rect of the row's text that follows the marker in the document (the text it labels), else the first one before it.
  const wordRect = (row, skip) => {
    for (const after of [true, false]) {
      const q = wordRectIn(row, skip, after); if (q) return q;
    }
    return null;
  };
  const wordRectIn = (row, skip, after) => {
    const tw = document.createTreeWalker(row, NodeFilter.SHOW_TEXT); let n;
    while ((n = tw.nextNode())) {
      if (!n.textContent.trim() || (skip && skip.contains(n)) || (skip && !!(skip.compareDocumentPosition(n) & 4) !== after) || n.parentElement.closest("svg,code,pre,[aria-hidden=true],script,style")) continue;
      const m = /\S+/.exec(n.textContent), g = document.createRange(); g.setStart(n, m.index); g.setEnd(n, m.index + m[0].length);
      const q = [...g.getClientRects()].find((x) => x.width > 0); if (q) return q;
    }
    return null;
  };
  const markerIn = (row) => {
    let level = [...row.children];
    for (let d = 0; d < 3 && level.length; d++) {
      for (const m of level) {
        if (!visible(m)) continue;
        const r = m.getBoundingClientRect(), s = getComputedStyle(m), t = (m.innerText || "").trim();
        const dot = r.width >= 2 && r.height >= 2 && r.width <= 20 && r.height <= 20 && !t;
        const rad = parseFloat(s.borderTopLeftRadius) * (/%/.test(s.borderTopLeftRadius) ? Math.min(r.width, r.height) / 100 : 1);
        const badge = /^\d{1,3}$/.test(t) && r.width <= 40 && Math.abs(r.width - r.height) <= 1 && rad >= Math.min(r.width, r.height) / 2 - 1;
        if (!dot && !badge) continue;
        const q = wordRect(row, m); if (!q) return null;
        const cy = (q.top + q.bottom) / 2;
        if (Math.abs((r.top + r.bottom) / 2 - cy) > 14) continue; // stacked or bottom-aligned: not a bullet
        return { el: m, cx: (r.left + r.right) / 2, cy: (r.top + r.bottom) / 2, line: cy };
      }
      level = level.flatMap((m) => [...m.children]);
    }
    return null;
  };
  const pseudoLine = (el, which) => {
    const s = getComputedStyle(el, which), w = parseFloat(s.width), h = parseFloat(s.height);
    if (s.content === "none" || s.content === "normal" || s.position !== "absolute" || !(w > 0 && w <= 3) || !(h > 0)) return null;
    let cbe = el; while (cbe && getComputedStyle(cbe).position === "static") cbe = cbe.parentElement;
    const cr = (cbe || document.documentElement).getBoundingClientRect(), cc = cbe ? getComputedStyle(cbe) : null, bw = (k) => (cc ? parseFloat(cc["border" + k + "Width"]) : 0);
    const tm = /^matrix\(([^)]+)\)/.exec(s.transform), tx = tm ? +tm[1].split(",")[4] : 0, ty = tm ? +tm[1].split(",")[5] : 0;
    const x = s.left !== "auto" ? cr.left + bw("Left") + parseFloat(s.left) : s.right !== "auto" ? cr.right - bw("Right") - parseFloat(s.right) - w : NaN;
    const y = s.top !== "auto" ? cr.top + bw("Top") + parseFloat(s.top) : s.bottom !== "auto" ? cr.bottom - bw("Bottom") - parseFloat(s.bottom) - h : NaN;
    return isNaN(x) || isNaN(y) ? null : { cx: x + tx + w / 2, y0: y + ty, y1: y + ty + h };
  };
  for (const list of document.querySelectorAll("body *")) {
    if (list.children.length < 3 || list.children.length > 60 || !visible(list) || list.closest("svg,[aria-hidden=true],[data-lb-ignore]")) continue;
    // Repeated rows: same tag and same number of children (a card's mixed parts are not rows).
    const sets = {};
    for (const row of [...list.children].filter(visible)) { const mk = markerIn(row); if (mk) (sets[row.tagName + row.children.length] = sets[row.tagName + row.children.length] || []).push({ row, mk }); }
    const rows = Object.values(sets).sort((a, b) => b.length - a.length)[0] || [];
    if (rows.length < 3) continue;
    const name = selOf(list), put = (reason, delta, row) => out.push({ type: "MARKER", reason, delta: Math.round(delta * 10) / 10 + "px", text: labelOf(row), sel: name });
    const x0 = rows[0].mk.cx;
    for (const { row, mk } of rows) {
      if (Math.abs(mk.cx - x0) > 1) put("x-off", mk.cx - x0, row);
      if (Math.abs(mk.cy - mk.line) > 2) put("y-off", mk.cy - mk.line, row);
    }
    const first = rows[0].mk.cy, last = rows[rows.length - 1].mk.cy;
    const lines = [];
    for (const [host, which] of [[list, "::before"], [list, "::after"], ...rows.flatMap((x) => [[x.row, "::before"], [x.row, "::after"]])]) {
      const p = pseudoLine(host, which); if (p) lines.push({ ...p, top: host === list, pseudoRow: host !== list, name: which });
    }
    for (const el of [...list.children, ...rows.flatMap((x) => [...x.row.children])]) {
      if (rows.some((x) => x.mk.el === el)) continue;
      const r = el.getBoundingClientRect();
      if (r.width > 0 && r.width <= 3 && r.height >= 12 && visible(el) && !(el.innerText || "").trim()) lines.push({ cx: (r.left + r.right) / 2, y0: r.top, y1: r.bottom, top: el.parentElement === list, name: "thin" });
    }
    // Only a line that runs through markers is a connector (a divider or border inside a row is not): 2+ for a list line or element, 1 for a row's own pseudo.
    const cover = (L) => rows.filter((x) => x.mk.cy >= L.y0 - 1 && x.mk.cy <= L.y1 + 1).length;
    for (const L of lines.filter((l) => cover(l) >= (l.pseudoRow ? 1 : 2))) {
      if (Math.abs(L.cx - x0) > 1) put("line-x " + L.name, L.cx - x0, rows[0].row);
      else if (L.top && (Math.abs(L.y0 - first) > 2 || Math.abs(L.y1 - last) > 2)) put("line-ends " + L.name, Math.abs(L.y0 - first) > 2 ? L.y0 - first : L.y1 - last, rows[0].row);
    }
  }
  // SHRUNK: an element whose inline font-size a script changed after load (recorded by the init script below).
  for (const el of window.__lbFS || []) {
    if (!el.isConnected || !el.style.fontSize || !visible(el)) continue;
    const text = (el.innerText || "").replace(/\s+/g, " ").trim().slice(0, 70);
    if (text) out.push({ type: "SHRUNK", size: getComputedStyle(el).fontSize, text, sel: el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") + (el.classList.length ? "." + [...el.classList].slice(0, 2).join(".") : "") });
  }
  return out;
}

// STRESS: runs inside the page. Mutates the live DOM (kind: long-text, long-token, big-numbers, empty; null = leave it as is),
// then returns layout breakage only, never copy rules: page overflow, a child past its parent's box, text past its own box,
// text clipped by overflow hidden, overlapping sibling text. The caller reloads the page before the next kind.
function stressPage({ kind, max }) {
  const TOKEN = "longname.surname.department@company.test"; // 40 characters, no break opportunity
  const skipped = (el) => !!el.closest("script,style,noscript,code,pre,kbd,samp,textarea,input,select,option,svg,math,[aria-hidden=true],[data-lb-ignore]");
  const shown = (el) => { const s = getComputedStyle(el); if (s.visibility === "hidden" || s.display === "none" || s.display === "contents" || +s.opacity === 0) return false; const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const own = (el) => [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim());
  const sel = (el) => el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") + (typeof el.className === "string" && el.className.trim() ? "." + el.className.trim().split(/\s+/).slice(0, 2).join(".") : "");
  const leaves = () => [...document.body.querySelectorAll("*")].filter((el) => own(el).length && !skipped(el) && shown(el));
  // At most `max` elements, one per tag and class first (so chips, cells, buttons and headings are all hit), then spread over the rest.
  const spread = (a, n) => (a.length <= n ? a : Array.from({ length: n }, (_, i) => a[Math.floor((i * a.length) / n)]));
  const pick = (els) => {
    const seen = new Set(), first = [], rest = [];
    for (const el of els) { const k = el.tagName + "|" + el.className; (seen.has(k) ? rest : first).push(el); seen.add(k); }
    return first.length >= max ? spread(first, max) : first.concat(spread(rest, max - first.length));
  };

  let n = 0;
  if (kind === "long-text") for (const el of pick(leaves())) { for (const t of own(el)) { const s = t.textContent.trim(); t.textContent = s + " " + s; } n++; }
  if (kind === "long-token") for (const el of pick(leaves())) { own(el)[0].textContent += " " + TOKEN; n++; }
  if (kind === "big-numbers") for (const el of pick(leaves().filter((e) => own(e).some((t) => /\d/.test(t.textContent))))) { for (const t of own(el)) t.textContent = t.textContent.replace(/\d+/g, "987654321"); n++; }
  if (kind === "empty") {
    for (const c of spread([...document.querySelectorAll("ul,ol,tbody,[role=list]")].filter((e) => !skipped(e) && shown(e)), max)) {
      const tw = document.createTreeWalker(c, NodeFilter.SHOW_TEXT); let t;
      while ((t = tw.nextNode())) t.textContent = "";
      n++;
    }
  }
  if (kind && !n) return { n, hits: [] };

  const hits = [];
  const add = (reason, el, text) => hits.push({ type: "STRESS", kind: kind || "as-is", reason, sel: sel(el), text: (text == null ? el.innerText || "" : text).replace(/\s+/g, " ").trim().slice(0, 50) });
  const pos = (s) => s.position === "absolute" || s.position === "fixed";
  const scrolls = (el) => { for (let a = el; a && a !== document.body; a = a.parentElement) if (/(auto|scroll)/.test(getComputedStyle(a).overflowX)) return true; return false; };
  const clipped = (el) => { for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) if (getComputedStyle(a).overflowX !== "visible") return true; return false; };
  const all = [...document.body.querySelectorAll("*")].filter((el) => !skipped(el) && shown(el));
  const box = (el) => { let b = null; for (const t of own(el)) { const g = document.createRange(); g.selectNodeContents(t); const r = g.getBoundingClientRect(); b = b ? { left: Math.min(b.left, r.left), top: Math.min(b.top, r.top), right: Math.max(b.right, r.right), bottom: Math.max(b.bottom, r.bottom) } : r; } return b; };

  // Page overflow: the document scrolls sideways. Name the element that reaches furthest.
  if (document.documentElement.scrollWidth > innerWidth + 1) {
    let worst = null, ext = 2;
    for (const el of all) {
      if (getComputedStyle(el).position === "fixed" || clipped(el)) continue;
      const r = el.getBoundingClientRect(), x = Math.max(Math.max(r.right, r.left + el.scrollWidth) - innerWidth, -Math.min(r.left, r.right - el.scrollWidth));
      if (x >= ext) { ext = x; worst = el; } // >=: on a tie the deeper element wins
    }
    add("page-overflow", worst || document.documentElement, `${document.documentElement.scrollWidth}px wide in ${innerWidth}px`);
  }
  for (const el of all) {
    const cs = getComputedStyle(el), r = el.getBoundingClientRect(), p = el.parentElement;
    if (pos(cs) || scrolls(el)) continue;
    // A child past its parent's content box, where the parent neither clips nor scrolls.
    if (p && p !== document.body && p !== document.documentElement) {
      const ps = getComputedStyle(p), pr = p.getBoundingClientRect();
      if (ps.overflowX === "visible" && ps.display !== "inline" && ps.display !== "contents" && pr.width > 0) {
        const rtl = ps.direction === "rtl";
        const past = rtl ? pr.left + parseFloat(ps.borderLeftWidth) + parseFloat(ps.paddingLeft) - r.left : r.right - (pr.right - parseFloat(ps.borderRightWidth) - parseFloat(ps.paddingRight));
        if (past > 2) add("past-parent", el, undefined);
      }
    }
    if (!own(el).length || cs.display === "inline" || r.width <= 2 || !(el.innerText || "").trim()) continue; // no rendered text (visually hidden): nothing to clip
    // Text past its own box (nowrap in a fixed width, or a token that cannot break), or cut off by overflow hidden without an ellipsis.
    // Measured by the glyph boxes against the border box edge, not by scrollWidth, which counts padding as overflow.
    const b = box(el), bw = (side) => parseFloat(cs["border" + side + "Width"]);
    const sideways = Math.max(b.right - (r.right - bw("Right")), r.left + bw("Left") - b.left) > 2;
    if (/(hidden|clip)/.test(cs.overflowX)) {
      const lines = parseFloat(cs.webkitLineClamp) > 0;
      const down = !lines && /(hidden|clip)/.test(cs.overflowY) && b.bottom > r.bottom - bw("Bottom") + 2;
      if (cs.textOverflow !== "ellipsis" && (sideways || down)) add("clipped", el, undefined);
    } else if (cs.overflowX === "visible" && sideways) add("past-own-box", el, undefined);
  }
  // Overlap: text of two siblings drawn over each other (compared by the glyph boxes, so spilled text counts).
  const kids = new Map();
  for (const el of all) { const cs = getComputedStyle(el); if (own(el).length && !pos(cs) && cs.transform === "none") (kids.get(el.parentElement) || kids.set(el.parentElement, []).get(el.parentElement)).push(el); }
  for (const list of kids.values()) {
    const s = list.slice(0, 40).map((el) => ({ el, b: box(el) }));
    for (let i = 0; i < s.length; i++) for (let j = i + 1; j < s.length; j++) {
      const a = s[i].b, c = s[j].b;
      // Vertical overlap must be a real share of the line: tight headings (line-height near 1) overlap their neighbours' glyph boxes by a few px by design.
      if (Math.min(a.right, c.right) - Math.max(a.left, c.left) > 4 && Math.min(a.bottom, c.bottom) - Math.max(a.top, c.top) > 0.4 * Math.min(a.bottom - a.top, c.bottom - c.top))
        add("overlap", s[j].el, (s[i].el.innerText || "").trim().slice(0, 20) + " | " + (s[j].el.innerText || "").trim().slice(0, 20));
    }
  }
  return { n, hits };
}

// Runs before page scripts in every context: records elements whose inline font-size changed after load (static HTML is not recorded).
function trackFontSize() {
  const S = (window.__lbFS = new Set()), fs = (t) => (/font-size\s*:\s*([^;]+)/.exec(t || "") || [])[1];
  new MutationObserver((ms) => { for (const m of ms) if (m.target.style && m.target.style.fontSize && m.target.style.fontSize !== (fs(m.oldValue) || "").trim()) S.add(m.target); })
    .observe(document, { subtree: true, attributes: true, attributeFilter: ["style"], attributeOldValue: true });
}

// Hash-routed views (#/x, #!/x) are distinct pages; a plain #anchor is not. Stripping every hash once collapsed
// a 47-view single-page blueprint into its first view and reported CLEAN on 1 page (8 Oct 2026).
const isRoute = (x) => /^#!?\/./.test(x.hash);
const docOf = (u) => { const x = new URL(u); x.hash = ""; return x.href; };
const norm = (x) => { x = new URL(x); x.hash = isRoute(x) ? x.hash.replace(/\/+$/, "") : ""; return x.href; };

// Runs in the page: every link href plus [data-route] values (turned into hashes), for crawling and the coverage warning.
function links() {
  const rt = (v) => (v.startsWith("#") ? v : "#" + (v.startsWith("/") ? v : "/" + v));
  return [...document.querySelectorAll("a[href],[data-route]")].map((e) => (e.hasAttribute("data-route") ? rt(e.getAttribute("data-route")) : e.href));
}

// Opens u. Another hash route of the document already open is shown by switching the hash (no reload); returns true then.
async function show(page, u) {
  const x = new URL(u), doc = docOf(u);
  if (page._doc === doc && isRoute(x)) { await page.evaluate((h) => { location.hash = h; }, x.hash); await page.waitForTimeout(200); return true; }
  const res = await page.goto(u, { waitUntil: "networkidle", timeout: 45000 });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  page._doc = doc;
  return res;
}

const STRESS_KINDS = ["long-text", "long-token", "big-numbers", "empty"];

// Loads e.url from scratch (via about:blank, so a hash-only change still reloads) and replays its steps.
async function load(page, e) {
  await page.goto("about:blank");
  page._doc = null;
  await show(page, e.url);
  for (const s of e.steps) {
    if (s.startsWith("click:")) await page.click(s.slice(6));
    else if (s.startsWith("wait:")) await page.waitForTimeout(+s.slice(5));
  }
  await page.waitForTimeout(300);
}

// STRESS pass for one page at one width, in its own context: the page as is, then each mutation on a fresh load.
// Breakage that exists as is prints once (kind as-is); a mutation reports only what it adds.
async function stress(browser, e, ctxOpts) {
  const ctx = await browser.newContext(ctxOpts), page = await ctx.newPage(), hits = [];
  try {
    await load(page, e);
    const base = new Map();
    for (const h of (await page.evaluate(stressPage, { kind: null, max: 30 })).hits) { hits.push(h); const k = h.reason + "|" + h.sel; base.set(k, (base.get(k) || 0) + 1); }
    for (const kind of STRESS_KINDS) {
      await load(page, e);
      const seen = new Map(base);
      for (const h of (await page.evaluate(stressPage, { kind, max: 30 })).hits) {
        const k = h.reason + "|" + h.sel;
        if (seen.get(k) > 0) { seen.set(k, seen.get(k) - 1); continue; }
        hits.push(h);
      }
    }
  } finally { await ctx.close().catch(() => {}); }
  return hits;
}

// Tab through up to 20 focusable elements; each needs a visible change on :focus-visible (outline, box-shadow, border, background or underline).
async function focusHits(page) {
  await page.evaluate(() => {
    const st = document.createElement("style"); st.textContent = "*,*::before,*::after{transition:none!important;animation:none!important}"; document.head.appendChild(st);
    const sig = (e) => { const s = getComputedStyle(e); return [s.outlineStyle, s.outlineWidth, s.outlineColor, s.boxShadow, s.borderTopColor, s.borderRightColor, s.borderBottomColor, s.borderLeftColor, s.borderTopWidth, s.borderBottomWidth, s.backgroundColor, s.textDecorationLine].join("|"); };
    const els = [...document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,summary,[tabindex]:not([tabindex="-1"]),[role=button]')].filter((e) => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && !e.disabled; });
    window.__lbF = { els, sig, before: els.map(sig) };
    if (document.activeElement) document.activeElement.blur();
    scrollTo(0, 0);
  });
  const out = [], seen = new Set();
  for (let n = 0; n < 20; n++) {
    await page.keyboard.press("Tab");
    const r = await page.evaluate(() => {
      const F = window.__lbF, a = document.activeElement, i = F.els.indexOf(a);
      if (a === document.body || a === document.documentElement) return { end: true };
      if (i < 0) return { skip: true };
      const seg = (x) => x.tagName.toLowerCase() + (x.id ? "#" + x.id : "") + (typeof x.className === "string" && x.className.trim() ? "." + x.className.trim().split(/\s+/).slice(0, 2).join(".") : "");
      return { i, same: F.sig(a) === F.before[i], sel: seg(a.parentElement && a.parentElement !== document.body ? a.parentElement : a) + " > " + seg(a), text: (a.innerText || a.getAttribute("aria-label") || a.value || "").replace(/\s+/g, " ").trim().slice(0, 60) };
    });
    if (r.end || seen.has(r.i)) break;
    if (r.skip) continue;
    seen.add(r.i);
    if (r.same) out.push({ type: "A11Y", reason: "focus", sel: r.sel, text: r.text, info: "no outline, box-shadow, border, background or underline change on Tab focus" });
  }
  return out;
}

// Same-site links that answer 404 or 410. HEAD first, GET when the server refuses HEAD. One request per URL for the whole run, at most 200.
async function brokenLinks(page, links, cache) {
  const out = [], here = new URL(page.url());
  for (const l of links) {
    let x; try { x = new URL(l.href); } catch { continue; }
    if (isRoute(x) || /^(mailto|tel|javascript|data|blob):/i.test(l.raw || "") || /logout|signout|sign-out/i.test(x.pathname)) continue;
    x.hash = "";
    const key = x.href;
    let st = cache.get(key);
    if (st === undefined) {
      if (x.protocol === "file:" && here.protocol === "file:") {
        let f = ""; try { f = decodeURIComponent(x.pathname); } catch {}
        st = fs.existsSync(f) && (!fs.statSync(f).isDirectory() || fs.existsSync(path.join(f, "index.html"))) ? 200 : 404;
      } else if (x.origin === here.origin && /^https?:$/.test(x.protocol) && cache.size < 200) {
        try {
          let res = await page.request.fetch(key, { method: "HEAD", failOnStatusCode: false, maxRedirects: 5, timeout: 15000 });
          if (res.status() >= 400) res = await page.request.get(key, { failOnStatusCode: false, maxRedirects: 5, timeout: 15000 });
          st = res.status();
        } catch { st = 0; }
      } else continue;
      cache.set(key, st);
    }
    if (st === 404 || st === 410) out.push({ type: "BROKEN", reason: "link-" + st, sel: l.sel, text: l.text || l.raw, info: `${st} ${key}` });
  }
  return out;
}

async function crawl(page, base, max) {
  const origin = new URL(base).origin, seen = new Set(), queue = [base], found = [];
  while (queue.length && found.length < max) {
    const u = queue.shift();
    if (seen.has(u)) continue;
    seen.add(u);
    // A hash route is a view of a single-page app: its navigation is same-document and has no response.
    try { const res = await show(page, u); if (res === null ? !isRoute(new URL(u)) : res !== true && res.status() >= 400) continue; } catch { continue; }
    found.push(u);
    for (const l of await page.evaluate(links)) {
      const k = norm(new URL(l, u).href), x = new URL(k);
      if (x.origin === origin && !/logout|signout|sign-out|\.(pdf|zip|png|jpe?g|svg|webp|mp4)$/i.test(x.pathname) && !seen.has(k)) queue.push(k);
    }
  }
  return { found, left: new Set(queue.filter((q) => !seen.has(q))).size };
}

async function run() {
  const ctxOpts = (e, w) => ({ viewport: { width: w, height: 900 }, reducedMotion: "reduce", ...(e.role ? { storageState: auth[e.role] } : {}) });
  const base = opt("base");
  if (!base) throw new Error("--base is required");
  const widths = opt("widths", "375,768,1440").split(",").map(Number);
  const MIN = parseFloat(opt("min", "0.3"));
  const auth = Object.fromEntries(many("auth").map((a) => a.split("=")));
  const warnings = [];
  let entries = [];
  if (opt("urls")) {
    entries = fs.readFileSync(opt("urls"), "utf8").split("\n").map((s) => s.trim()).filter((s) => s && !s.startsWith("#")).map((line) => {
      let role = null;
      if (line.startsWith("@")) { role = line.slice(1, line.indexOf(" ")); line = line.slice(line.indexOf(" ") + 1).trim(); }
      const [u, ...steps] = line.split("|").map((s) => s.trim());
      return { role, url: new URL(u, base).href, steps };
    });
  }
  const browser = await launch();
  let stressOn = has("stress") || has("stress-all");
  if (has("crawl") || !entries.length) {
    const max = parseInt(opt("max", "300"));
    for (const role of [null, ...Object.keys(auth)]) {
      const ctx = await browser.newContext(role ? { storageState: auth[role] } : {});
      await ctx.addInitScript(trackFontSize);
      const pg = await ctx.newPage();
      const start = role && opt("start-" + role) ? new URL(opt("start-" + role), base).href : base;
      const { found, left } = await crawl(pg, start, max);
      for (const u of found) entries.push({ role, url: u, steps: [] });
      if (left) warnings.push(`WARNING crawl stopped at --max ${max}, ${left} queued pages not scanned`);
      await ctx.close();
    }
  }
  if (stressOn && entries.length > 20 && !has("stress-all")) { stressOn = false; warnings.push(`WARNING stress skipped: ${entries.length} pages is over 20 (add --stress-all to stress every page)`); }
  const stressAt = stressOn ? widths.filter((x) => x === 375 || x === 1440) : [];
  const report = [], uniq = new Map(), shared = new Map(), scanned = new Set(entries.map((e) => norm(e.url))), missing = new Set();
  let raw = 0, contrastSkipped = 0;
  const linkCache = new Map();
  for (const e of entries) {
    // Hash routes of one document share one page per width and switch views; everything else gets a fresh context.
    const route = isRoute(new URL(e.url)) && !e.steps.length;
    for (const w of widths) {
      const key = `${e.role}|${docOf(e.url)}|${w}`;
      let h = route && shared.get(key);
      if (!h) {
        // reducedMotion: scroll-reveal sections sit at opacity 0 until scrolled into view, and an invisible block is skipped, so everything below the fold went unchecked.
        const ctx = await browser.newContext(ctxOpts(e, w));
        await ctx.addInitScript(trackFontSize);
        h = { ctx, page: await ctx.newPage(), log: [] };
        h.page.on("console", (m) => { if (m.type() === "error") h.log.push({ reason: "console", text: m.text().slice(0, 90), info: m.location().url || "" }); });
        h.page.on("pageerror", (err) => h.log.push({ reason: "pageerror", text: String(err.message).split("\n")[0].slice(0, 90), info: "uncaught error" }));
        if (route) shared.set(key, h);
      }
      const page = h.page;
      try {
        h.log.length = 0;
        const res = await show(page, e.url);
        for (const s of e.steps) {
          if (s.startsWith("click:")) await page.click(s.slice(6));
          else if (s.startsWith("wait:")) await page.waitForTimeout(+s.slice(5));
        }
        if (res !== true) await page.waitForTimeout(300);
        if (w === widths[0]) for (const l of await page.evaluate(links)) { const x = new URL(l, e.url); if (isRoute(x) && docOf(x.href) === docOf(e.url) && !scanned.has(norm(x.href))) missing.add(norm(x.href)); }
        const hits = await page.evaluate(inspect, MIN);
        const pc = await page.evaluate(inspectPage, { w });
        hits.push(...pc.hits);
        contrastSkipped += pc.warn.contrast;
        hits.push(...h.log.map((l) => ({ type: "BROKEN", sel: "page", ...l })));
        if (w === widths[0]) hits.push(...(await brokenLinks(page, pc.links, linkCache)));
        if (stressAt.includes(w)) {
          try { hits.push(...(await stress(browser, e, ctxOpts(e, w)))); } catch (err) {
            console.log(`ERROR   ${w}px ${e.url}  stress: ${err.message.split("\n")[0]}`);
            report.push({ url: e.url, width: w, type: "ERROR", text: "stress: " + err.message.split("\n")[0] });
          }
        }
        hits.push(...(await focusHits(page)));
        const dir = await page.evaluate(() => document.documentElement.dir || getComputedStyle(document.body).direction);
        for (const x of hits) {
          raw++;
          report.push({ url: e.url, role: e.role || "public", width: w, dir, ...x });
          // The same defect on many views (a shared drawer or footer) prints once; the --out JSON keeps every hit.
          const k = [x.type, w, x.sel, x.text, x.tail || "", x.kind || "", x.reason || ""].join("\u0001");
          if (uniq.has(k)) { uniq.get(k).more++; continue; }
          const head = `${x.type.padEnd(7)} ${w}px ${e.role ? "@" + e.role + " " : ""}${e.url}  ${x.kind ? "[" + x.kind + " " + x.reason + "]  " : x.reason ? "[" + x.reason + "]  " : ""}${x.sel}  "${x.text}"${x.tail ? "  -> [" + x.tail + "] " + x.last : ""}${x.counts ? "  " + JSON.stringify(x.counts) : ""}${x.size ? "  " + x.size : ""}${x.info ? "  " + x.info : ""}`;
          uniq.set(k, { head: `${x.type} ${w}px ${x.kind ? "[" + x.kind + " " + x.reason + "] " : x.reason ? "[" + x.reason + "] " : ""}${x.sel} "${x.text}"`, more: 0 });
          console.log(head);
        }
      } catch (err) {
        console.log(`ERROR   ${w}px ${e.url}  ${err.message.split("\n")[0]}`);
        report.push({ url: e.url, width: w, type: "ERROR", text: err.message.split("\n")[0] });
        if (route) shared.delete(key);
        await h.ctx.close().catch(() => {});
        continue;
      }
      if (!route) await h.ctx.close();
    }
  }
  for (const h of shared.values()) await h.ctx.close();
  await browser.close();
  if (contrastSkipped) warnings.push("WARNING contrast not computed for text over images or other painted boxes (look at it)"), console.log(`NOTE   contrast skipped for ${contrastSkipped} text blocks over url() images or boxes painted behind them`);
  if (missing.size) warnings.push(`WARNING ${missing.size} in-page routes were not scanned (use --crawl or --urls)`);
  for (const u of uniq.values()) if (u.more) console.log(`  also on ${u.more} more routes: ${u.head}`);
  if (opt("out")) fs.writeFileSync(opt("out"), JSON.stringify(report, null, 2));
  const by = {};
  for (const u of uniq.keys()) { const t = u.split("\u0001")[0]; by[t] = (by[t] || 0) + 1; }
  for (const r of report) if (r.type === "ERROR") by.ERROR = (by.ERROR || 0) + 1;
  const routes = new Set(entries.filter((e) => isRoute(new URL(e.url))).map((e) => norm(e.url))).size;
  console.log("");
  for (const m of warnings) console.log(m);
  console.log(`PAGES ${entries.length}  WIDTHS ${widths.join(",")}${routes ? "  ROUTES " + routes : ""}${stressAt.length ? "  STRESS " + stressAt.join(",") : ""}  ${JSON.stringify(by)}`);
  console.log("FLAGGED", uniq.size);
  console.log("ROUTE-HITS", raw);
  process.exit(uniq.size ? 1 : 0);
}

(argv[0] === "login" ? login() : run()).catch((e) => { console.error(e.message); process.exit(2); });
