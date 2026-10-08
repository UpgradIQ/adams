#!/usr/bin/env node
// Line balance check for live web pages (sites, SaaS dashboards, academies), English and Arabic.
//
// Usage:
//   node web_balance.js --base https://site.com [--urls urls.txt] [--crawl] [--max 300]
//        [--widths 375,768,1440] [--auth role=state.json ...] [--min 0.5] [--out report.json]
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
// Exit code 1 when anything is flagged.
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
    if (!ownText && blockKids.length === 0 && kids.length && isBlockish(el) && (el.innerText || "").trim()) { blocks.push(el); return; }
    kids.forEach(walk);
  };
  walk(document.body);

  const out = [];
  const meta = [];
  for (const el of blocks) {
    // Collect one rect per word (works for LTR and RTL, since we only use geometry).
    const words = [];
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = tw.nextNode())) {
      if (n.parentElement.closest("code,pre,svg,[aria-hidden=true]")) continue;
      const re = /\S+/g; let m;
      while ((m = re.exec(n.textContent))) {
        const r = document.createRange(); r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length);
        const rects = [...r.getClientRects()].filter((q) => q.width > 0);
        if (rects.length) words.push({ t: m[0], top: rects[0].top, l: Math.min(...rects.map((q) => q.left)), r: Math.max(...rects.map((q) => q.right)), h: rects[0].height });
      }
    }
    if (!words.length) continue;
    const lines = [];
    for (const w of words) {
      const L = lines.find((x) => Math.abs(x.top - w.top) < w.h * 0.5);
      if (L) { L.l = Math.min(L.l, w.l); L.r = Math.max(L.r, w.r); L.words.push(w.t); }
      else lines.push({ top: w.top, l: w.l, r: w.r, words: [w.t] });
    }
    lines.sort((a, b) => a.top - b.top);
    const text = (el.innerText || "").replace(/\s+/g, " ").trim().slice(0, 70);
    const tag = el.tagName;
    const cs = getComputedStyle(el);
    const sel = tag.toLowerCase() + (el.id ? "#" + el.id : "") + (el.classList.length ? "." + [...el.classList].slice(0, 2).join(".") : "");
    const rect = el.getBoundingClientRect();
    meta.push({ key: `${Math.round(rect.top / 3)}|${tag}|${el.className}|${cs.fontSize}`, n: lines.length, text, sel });
    if (lines.length < 2) continue;
    const isShort = SHORT.has(tag) || el.closest("li,button,label,th,nav,[role=tab],[role=button],[class*=badge],[class*=chip],[class*=pill],[class*=tag]");
    if (tag === "H1") { if (lines.length > 2) out.push({ type: "HERO", lines: lines.length, text, sel }); continue; }
    if (isShort && words.length <= 8) { out.push({ type: "WRAPPED", lines: lines.length, text, sel }); continue; }
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
  return out;
}

async function crawl(page, base, max) {
  const origin = new URL(base).origin, seen = new Set(), queue = [base], found = [];
  while (queue.length && found.length < max) {
    const u = queue.shift();
    if (seen.has(u)) continue;
    seen.add(u);
    try { const res = await page.goto(u, { waitUntil: "networkidle", timeout: 30000 }); if (!res || res.status() >= 400) continue; } catch { continue; }
    found.push(u);
    const links = await page.$$eval("a[href]", (as) => as.map((a) => a.href));
    for (const l of links) {
      const x = new URL(l, u); x.hash = "";
      if (x.origin === origin && !/logout|signout|sign-out|\.(pdf|zip|png|jpe?g|svg|webp|mp4)$/i.test(x.pathname) && !seen.has(x.href)) queue.push(x.href);
    }
  }
  return found;
}

async function run() {
  const base = opt("base");
  if (!base) throw new Error("--base is required");
  const widths = opt("widths", "375,768,1440").split(",").map(Number);
  const MIN = parseFloat(opt("min", "0.5"));
  const auth = Object.fromEntries(many("auth").map((a) => a.split("=")));
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
  if (has("crawl") || !entries.length) {
    for (const role of [null, ...Object.keys(auth)]) {
      const ctx = await browser.newContext(role ? { storageState: auth[role] } : {});
      const pg = await ctx.newPage();
      const start = role && opt("start-" + role) ? new URL(opt("start-" + role), base).href : base;
      for (const u of await crawl(pg, start, parseInt(opt("max", "300")))) entries.push({ role, url: u, steps: [] });
      await ctx.close();
    }
  }
  const report = [];
  let total = 0;
  for (const e of entries) {
    for (const w of widths) {
      // reducedMotion: scroll-reveal sections sit at opacity 0 until scrolled into view, and an invisible block is skipped, so everything below the fold went unchecked.
      const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, reducedMotion: "reduce", ...(e.role ? { storageState: auth[e.role] } : {}) });
      const page = await ctx.newPage();
      try {
        await page.goto(e.url, { waitUntil: "networkidle", timeout: 45000 });
        await page.evaluate(() => document.fonts && document.fonts.ready);
        for (const s of e.steps) {
          if (s.startsWith("click:")) await page.click(s.slice(6));
          else if (s.startsWith("wait:")) await page.waitForTimeout(+s.slice(5));
        }
        await page.waitForTimeout(300);
        const hits = await page.evaluate(inspect, MIN);
        const dir = await page.evaluate(() => document.documentElement.dir || getComputedStyle(document.body).direction);
        for (const h of hits) {
          total++;
          report.push({ url: e.url, role: e.role || "public", width: w, dir, ...h });
          console.log(`${h.type.padEnd(7)} ${w}px ${e.role ? "@" + e.role + " " : ""}${e.url}  ${h.sel}  "${h.text}"${h.tail ? "  -> [" + h.tail + "] " + h.last : ""}${h.counts ? "  " + JSON.stringify(h.counts) : ""}`);
        }
      } catch (err) {
        console.log(`ERROR   ${w}px ${e.url}  ${err.message.split("\n")[0]}`);
        report.push({ url: e.url, width: w, type: "ERROR", text: err.message.split("\n")[0] });
      }
      await ctx.close();
    }
  }
  await browser.close();
  if (opt("out")) fs.writeFileSync(opt("out"), JSON.stringify(report, null, 2));
  const by = {};
  for (const r of report) by[r.type] = (by[r.type] || 0) + 1;
  console.log(`\nPAGES ${entries.length}  WIDTHS ${widths.join(",")}  ${JSON.stringify(by)}`);
  console.log("FLAGGED", total);
  process.exit(total ? 1 : 0);
}

(argv[0] === "login" ? login() : run()).catch((e) => { console.error(e.message); process.exit(2); });
