// Page checks for web_balance.js: eleven rules about what a page says and how it behaves, run at every width.
// inspectPage runs inside the page (it must stay self-contained, no outer variables). It returns { hits, warn, links }.
// Hit types: PLACEHOLDER COUNT GAP GAP-RHYTHM TABLE SUBLINE THIN A11Y BROKEN COPY COVER RTL.
// Roles come from tags, rendering and attributes, never from class names; the one exception is RTL icon detection.
// Shortcuts: bounding boxes, not outlines; at most 25 hits per type and reason on one page and width (a final "N more" hit says so).

function inspectPage({ w }) {
  const hits = [], warn = { contrast: 0 }, count = {}, over = {};
  const SKIP = "script,style,noscript,template,code,pre,kbd,samp,textarea,svg,[aria-hidden=true],[data-lb-ignore]";
  const HEADS = "h1,h2,h3,h4,h5,h6";
  const cs = (e) => getComputedStyle(e);
  const seg = (x) => x.tagName.toLowerCase() + (x.id ? "#" + x.id : "") + (typeof x.className === "string" && x.className.trim() ? "." + x.className.trim().split(/\s+/).slice(0, 2).join(".") : "");
  const pathOf = (el) => { const p = []; for (let a = el; a && a !== document.body && p.length < 3; a = a.parentElement) p.unshift(seg(a)); return p.join(" > ") || "body"; };
  const add = (type, reason, el, text, info) => {
    const k = type + "|" + reason;
    if ((count[k] = (count[k] || 0) + 1) > 25) { over[k] = (over[k] || 0) + 1; return; }
    hits.push({ type, reason, sel: pathOf(el), text: (text || "").replace(/\s+/g, " ").trim().slice(0, 60), info });
  };
  const run = (name, fn) => { try { fn(); } catch (e) { hits.push({ type: "CHECK-ERROR", reason: name, sel: "", text: name + " check crashed: " + String(e.message).slice(0, 80) }); } };
  const vcache = new WeakMap();
  const vis = (el) => {
    if (!el || el === document.documentElement || el === document.body) return true;
    if (vcache.has(el)) return vcache.get(el);
    const s = cs(el);
    let v = !(s.visibility === "hidden" || s.display === "none" || +s.opacity === 0);
    if (v && s.display === "contents") v = vis(el.parentElement);
    else if (v) { const r = el.getBoundingClientRect(); v = r.width > 0 && r.height > 0 && vis(el.parentElement); }
    vcache.set(el, v);
    return v;
  };
  // Every visible text node outside code, svg, textarea, aria-hidden and data-lb-ignore.
  const TN = [];
  { const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
    while ((n = tw.nextNode())) {
      if (!n.textContent.trim()) continue;
      const el = n.parentElement;
      if (!el || el.closest(SKIP) || !vis(el)) continue;
      TN.push({ n, el, t: n.textContent.replace(/\s+/g, " ").trim() });
    } }
  const own = (el) => [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim());
  const textRects = (el) => { const out = []; for (const n of own(el)) { const g = document.createRange(); g.selectNodeContents(n); out.push(...[...g.getClientRects()].filter((q) => q.width > 0)); } return out; };
  const textOf = (el) => (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim();
  const bgOf = (el) => { for (let a = el; a; a = a.parentElement) { const b = cs(a).backgroundColor; if (b !== "rgba(0, 0, 0, 0)" && b !== "transparent") return b; } return "rgb(255, 255, 255)"; };
  const boxed = (el) => { // a visible box of its own: border, shadow, image or a fill unlike its surroundings
    const s = cs(el);
    if (["Top", "Right", "Bottom", "Left"].some((k) => parseFloat(s["border" + k + "Width"]) > 0 && s["border" + k + "Style"] !== "none")) return true;
    if (s.boxShadow !== "none" || s.backgroundImage !== "none") return true;
    return s.backgroundColor !== "rgba(0, 0, 0, 0)" && s.backgroundColor !== "transparent" && el.parentElement && s.backgroundColor !== bgOf(el.parentElement);
  };

  // PLACEHOLDER: copy that was never filled in or a template that did not render.
  run("PLACEHOLDER", () => {
    const PH = [[/lorem ipsum/i, "lorem ipsum"], [/\bTODO\b/, "TODO"], [/\bFIXME\b/, "FIXME"], [/\bTBD\b/, "TBD"], [/\{\{|\}\}/, "{{ }}"], [/\bundefined\b/, "undefined"],
      [/\bNaN\b/, "NaN"], [/\bnull\b/, "null"], [/\[object Object\]/, "[object Object]"], [/\$\{/, "${"]];
    for (const { el, t } of TN) for (const [re, name] of PH) if (re.test(t)) { add("PLACEHOLDER", name, el, t, "visible text contains " + name); break; }
  });

  // COPY: dashes, exclamation marks in headings, buttons and labels, Title Case headings.
  run("COPY", () => {
    for (const { el, t } of TN) {
      const dash = t.match(new RegExp("[" + String.fromCharCode(8212, 8211) + "]"));
      if (dash) add("COPY", "dash", el, t, "contains U+" + dash[0].charCodeAt(0).toString(16).toUpperCase().padStart(4, "0") + ", use a comma, colon or a plain hyphen");
      if (t.includes("!") && el.closest(HEADS + ",button,[role=button],label,legend")) add("COPY", "exclamation", el, t, "exclamation mark in a heading, button or label");
    }
    for (const i of document.querySelectorAll("input[type=submit],input[type=button]")) if (vis(i) && /!/.test(i.value)) add("COPY", "exclamation", i, i.value, "exclamation mark in a button");
    // Words that are proper nouns: capitalized in the middle of a sentence somewhere else on the page.
    const clean = (x) => x.replace(/^[("'\u201c]+|[.,;:!?)"'\u201d]+$/g, "").replace(/['\u2019]s$/, "");
    const P = new Set();
    for (const { el, t } of TN) {
      if (el.closest(HEADS)) continue;
      const tk = t.split(" ");
      for (let i = 1; i < tk.length; i++) { const c = clean(tk[i]); if (/^\p{Lu}[\p{L}'-]*$/u.test(c) && !/[.!?:]$/.test(tk[i - 1])) P.add(c.toLowerCase()); }
    }
    for (const h of document.querySelectorAll(HEADS)) {
      if (!vis(h) || h.closest(SKIP.replace("svg,", ""))) continue;
      const text = textOf(h), words = text.split(" ").map(clean).filter((x) => /^\p{L}/u.test(x));
      if (words.length < 3) continue;
      const rest = words.slice(1).filter((x) => !/^\p{Lu}{2,}$/u.test(x) && !/\d/.test(x) && !/^.\p{Ll}*\p{Lu}/u.test(x) && !P.has(x.toLowerCase()));
      const caps = rest.filter((x) => /^\p{Lu}/u.test(x));
      if (rest.length >= 2 && caps.length / rest.length > 0.5) add("COPY", "title-case", h, text, caps.length + " of " + rest.length + " words after the first are capitalized, use sentence case");
    }
  });

  // COUNT: a heading that states a count ("Six principles", "3 steps") above a list or grid with another number of items.
  run("COUNT", () => {
    const NUM = { two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10, eleven: 11, twelve: 12 };
    const UNIT = /^(months?|weeks?|days?|hours?|minutes?|years?|seconds?|percent|times|min|sec)$/i;
    const IRR = /^(people|men|women|children|criteria|phenomena|data|media)$/i;
    // The list or grid a heading introduces: the first container of repeated siblings after it, before the next heading of its level or higher.
    const itemsOf = (x) => {
      if (!vis(x) || x.closest("nav,footer")) return null;
      if (x.tagName === "UL" || x.tagName === "OL" || x.getAttribute("role") === "list") { const k = [...x.children].filter(vis); return k.length >= 2 ? k : null; }
      const d = cs(x).display;
      if (!/grid|flex/.test(d)) return null;
      const k = [...x.children].filter((c) => vis(c) && !/absolute|fixed/.test(cs(c).position));
      return k.length >= 2 && k.every((c) => c.tagName === k[0].tagName && c.className === k[0].className) ? k : null;
    };
    const find = (root, level) => {
      const tw = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT); let e = root;
      do {
        if (/^H[1-6]$/.test(e.tagName) && +e.tagName[1] <= level) return null;
        const k = itemsOf(e); if (k) return { el: e, n: k.length };
      } while ((e = tw.nextNode()));
      return null;
    };
    for (const h of document.querySelectorAll(HEADS)) {
      if (!vis(h) || h.closest(SKIP.replace("svg,", ""))) continue;
      const m = /^\s*(?:the\s+)?(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|[2-9]|1[0-2])\s+([a-z-]+)(?:\s+([a-z-]+))?/i.exec(textOf(h));
      if (!m || UNIT.test(m[2])) continue;
      const plural = (x) => !!x && (/[^s]s$/i.test(x) || IRR.test(x));
      if (!plural(m[2]) && !plural(m[3])) continue;
      const want = NUM[m[1].toLowerCase()] || +m[1], level = +h.tagName[1], boundary = h.closest("section,article,main") || document.body;
      let found = null;
      for (let e = h, d = 0; e && e !== boundary && d < 4 && !found; e = e.parentElement, d++)
        for (let s = e.nextElementSibling; s && !found; s = s.nextElementSibling) { if (vis(s)) found = find(s, level); if (/^H[1-6]$/.test(s.tagName) && +s.tagName[1] <= level) break; }
      if (found && found.n !== want) add("COUNT", "heading-vs-list", h, textOf(h), "heading says " + want + ", " + seg(found.el) + " has " + found.n);
    }
  });

  // GAP: stacked sections must not touch; GAP-RHYTHM: the gaps between sections should repeat (at most two sizes, 2px tolerance).
  // The gap is what the eye sees: a box edge for a section with its own fill or border, else its outermost content.
  // Two full-width bands that touch are a design (bands), not a gap.
  run("GAP", () => {
    const flat = (c) => [...c.children].flatMap((k) => (cs(k).display === "contents" ? flat(k) : [k]));
    let host = document.querySelector("main") || document.body;
    const live = (c) => flat(c).filter((k) => !/^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE|HR)$/.test(k.tagName) && vis(k) && !/absolute|fixed/.test(cs(k).position));
    for (let i = 0; i < 3; i++) { const k = live(host); if (k.length === 1 && k[0].tagName === "DIV") host = k[0]; else break; }
    const secs = live(host).filter((k) => /^(SECTION|ARTICLE|ASIDE|HEADER|FOOTER|FORM|FIGURE)$/.test(k.tagName) || (k.tagName === "DIV" && k.getBoundingClientRect().height >= 120))
      .sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
    const inAbs = (e, root) => { for (let a = e; a && a !== root; a = a.parentElement) if (/absolute|fixed/.test(cs(a).position)) return true; return false; };
    const extent = (sec) => {
      let t = Infinity, b = -Infinity;
      const take = (r) => { if (r.width > 0 && r.height > 0) { t = Math.min(t, r.top); b = Math.max(b, r.bottom); } };
      const tw = document.createTreeWalker(sec, NodeFilter.SHOW_TEXT); let n;
      while ((n = tw.nextNode())) { const e = n.parentElement; if (!n.textContent.trim() || e.closest(SKIP.replace("svg,", "")) || !vis(e) || inAbs(e, sec)) continue; const g = document.createRange(); g.selectNodeContents(n); [...g.getClientRects()].forEach(take); }
      for (const e of sec.querySelectorAll("img,svg,video,canvas,iframe,input,button,select,textarea,table,*")) {
        if (!vis(e) || inAbs(e, sec)) continue;
        if (/^(IMG|SVG|VIDEO|CANVAS|IFRAME|INPUT|BUTTON|SELECT|TEXTAREA|TABLE)$/i.test(e.tagName) || (e !== sec && boxed(e) && e.getBoundingClientRect().height >= 24)) take(e.getBoundingClientRect());
      }
      return t === Infinity ? null : { t, b };
    };
    const cw = document.documentElement.clientWidth;
    const info = secs.map((e) => { const r = e.getBoundingClientRect(), bx = boxed(e), x = bx ? null : extent(e); return { e, r, bx, band: bx && r.width >= cw - 2, top: bx ? r.top : x && x.t, bot: bx ? r.bottom : x && x.b }; }).filter((s) => s.top != null);
    const gaps = [];
    for (let i = 0; i + 1 < info.length; i++) {
      const a = info[i], b = info[i + 1];
      if (a.band && b.band) continue;
      const gap = Math.round(b.top - a.bot);
      gaps.push({ gap, i });
      if (gap < 12) add("GAP", gap < 0 ? "overlap" : "touch", b.e, textOf(b.e).slice(0, 30), (gap < 0 ? "overlaps" : "only " + gap + "px below") + " the previous section (" + seg(a.e) + "), needs 12px or more");
    }
    // Rhythm: skip the first and last section.
    const mid = gaps.filter((g) => g.i >= 1 && g.i + 1 <= info.length - 2).map((g) => g.gap).sort((a, b) => a - b);
    if (mid.length >= 3) {
      const groups = []; for (const v of mid) { const g = groups[groups.length - 1]; if (g && v - g[g.length - 1] <= 2) g.push(v); else groups.push([v]); }
      if (groups.length > 2) add("GAP-RHYTHM", "rhythm", host, "", groups.length + " different gaps between sections: " + mid.join(", ") + "px");
    }
  });

  // TABLE: number columns right (end) aligned with tabular figures, text columns left (start) aligned, headers aligned with their column,
  // content 16px or more from the table frame. A header taking 2+ lines is WRAPPED unless it has over 8 words.
  run("TABLE", () => {
    const numRe = /^[+\-\u2212]?\s*[$\u20ac\u00a3\u00a5]?\s*[+\-\u2212]?\d[\d.,\s]*\s*(?:%|[kKmMbB]|[A-Z]{3}|ms|s)?$/;
    const phys = (x) => { const s = cs(x); let a = s.textAlign.replace(/^-(internal|webkit)-/, ""); if (a === "start") a = s.direction === "rtl" ? "right" : "left"; if (a === "end") a = s.direction === "rtl" ? "left" : "right"; return a; };
    const major = (a) => { const m = {}; a.forEach((x) => (m[x] = (m[x] || 0) + 1)); return Object.keys(m).sort((x, y) => m[y] - m[x])[0]; };
    const framedEl = (e) => { const s = cs(e); return ["Left", "Right", "Top", "Bottom"].some((k) => parseFloat(s["border" + k + "Width"]) > 0 && s["border" + k + "Style"] !== "none") || (s.backgroundColor !== "rgba(0, 0, 0, 0)" && s.backgroundColor !== "transparent"); };
    const contentRects = (c) => { // glyph boxes and media inside a cell
      const out = []; const tw = document.createTreeWalker(c, NodeFilter.SHOW_TEXT); let n;
      while ((n = tw.nextNode())) { if (!n.textContent.trim()) continue; const g = document.createRange(); g.selectNodeContents(n); out.push(...[...g.getClientRects()].filter((q) => q.width > 0)); }
      for (const e of c.querySelectorAll("img,svg,input,video,canvas")) { const r = e.getBoundingClientRect(); if (r.width > 0) out.push(r); }
      return out;
    };
    for (const t of document.querySelectorAll("table")) {
      if (!vis(t) || /^(presentation|none)$/.test(t.getAttribute("role") || "") || t.closest("[aria-hidden=true],[data-lb-ignore]")) continue;
      const rows = [...t.rows].filter(vis);
      if (rows.length < 2) continue;
      const hdr = rows.find((r) => r.cells.length && [...r.cells].every((c) => c.tagName === "TH"));
      const hdrShown = hdr && hdr.getBoundingClientRect().height > 2 && cs(hdr.parentElement).clipPath === "none";
      const body = rows.filter((r) => r !== hdr && [...r.cells].some((c) => c.tagName === "TD"));
      const spans = [...t.querySelectorAll("td,th")].some((c) => c.colSpan > 1 || c.rowSpan > 1);
      const rtl = cs(t).direction === "rtl", cols = Math.max(0, ...body.map((r) => r.cells.length));
      if (!spans) for (let c = 0; c < cols; c++) {
        const cells = body.map((r) => r.cells[c]).filter((x) => x && vis(x) && cs(x).display === "table-cell" && (x.innerText || "").trim());
        if (cells.length < 2) continue;
        const num = cells.filter((x) => numRe.test(x.innerText.trim())).length / cells.length >= 0.7;
        const want = num ? (rtl ? "left" : "right") : (rtl ? "right" : "left"), got = cells.map(phys);
        const th = hdrShown && hdr.cells[c], label = th ? textOf(th) : "col " + (c + 1);
        const bad = got.filter((a) => a !== want && !(a === "justify" && !num)).length;
        if (bad >= Math.ceil(cells.length / 2)) add("TABLE", num ? "num-align" : "text-align", t, label, (num ? "number" : "text") + " column " + (c + 1) + ": " + want + " expected, " + bad + " of " + cells.length + " cells " + major(got));
        else if (th && vis(th) && textOf(th) && phys(th) !== major(got)) add("TABLE", "th-align", t, label, "column " + (c + 1) + ": header " + phys(th) + ", cells " + major(got));
        if (num) { const tab = cells.filter((x) => { const s = cs(x); return /tabular-nums/.test(s.fontVariantNumeric) || /tnum/.test(s.fontFeatureSettings) || /mono/i.test(s.fontFamily); }).length; if (tab < cells.length / 2) add("TABLE", "tabular-nums", t, label, "number column " + (c + 1) + " lacks font-variant-numeric: tabular-nums"); }
      }
      if (hdrShown) for (const th of hdr.cells) {
        const words = textOf(th).split(" ").filter(Boolean).length;
        if (words > 8 && new Set(textRects(th).map((q) => Math.round(q.top))).size > 1) add("TABLE", "th-wrap", t, textOf(th), "header wraps onto 2+ lines");
      }
      // Inset from the visible frame: the table itself, else the nearest box with a border or fill (EDGE reports under 12px horizontally).
      let frame = t; while (frame && frame !== document.body && !framedEl(frame)) frame = frame.parentElement;
      if (!frame || frame === document.body) continue;
      const fr = frame.getBoundingClientRect(), fs = cs(frame), edge = { l: fr.left + parseFloat(fs.borderLeftWidth), r: fr.right - parseFloat(fs.borderRightWidth), t: fr.top + parseFloat(fs.borderTopWidth), b: fr.bottom - parseFloat(fs.borderBottomWidth) };
      const scrolls = (() => { for (let a = t.parentElement; a && a !== document.body; a = a.parentElement) if (/(auto|scroll)/.test(cs(a).overflowX) && a.scrollWidth > a.clientWidth + 1) return true; return false; })();
      const shownRows = rows.filter((r) => r.getBoundingClientRect().height > 2);
      let gl = Infinity, gr = Infinity;
      for (const r of shownRows) { const rs = [...r.cells].flatMap(contentRects); if (rs.length) { gl = Math.min(gl, Math.min(...rs.map((q) => q.left)) - edge.l); gr = Math.min(gr, edge.r - Math.max(...rs.map((q) => q.right))); } }
      const rect = (r) => { const rs = [...r.cells].flatMap(contentRects); return rs.length ? { t: Math.min(...rs.map((q) => q.top)), b: Math.max(...rs.map((q) => q.bottom)) } : null; };
      const first = shownRows.length && rect(shownRows[0]), last = shownRows.length && rect(shownRows[shownRows.length - 1]);
      const gx = Math.min(gl, gr);
      if (!scrolls && gx >= 12 && gx < 16) add("TABLE", "inset-x", t, textOf(t).slice(0, 30), "first or last column content is " + Math.round(gx) + "px from the frame, needs 16px");
      const top = first ? first.t - edge.t : Infinity, bot = last ? edge.b - last.b : Infinity;
      if (Math.min(top, bot) < 16) add("TABLE", "inset-y", t, textOf(t).slice(0, 30), "first row content is " + Math.round(top) + "px from the frame top, last row " + Math.round(bot) + "px from the bottom, needs 16px");
    }
  });

  // SUBLINE: a paragraph right after an h1 to h3 shares its start edge (centers if both centered) and is no wider than a width-limited heading.
  run("SUBLINE", () => {
    const firstLine = (el) => { // rects of the contents, so an inline box with padding (a code chip) counts from its edge
      const g = document.createRange(); g.selectNodeContents(el);
      const rs = [...g.getClientRects()].filter((q) => q.width > 0 && q.height > 0);
      if (!rs.length) return null;
      const top = Math.min(...rs.map((q) => q.top)), L = rs.filter((q) => Math.abs(q.top - top) < q.height * 0.5 + 4);
      return { l: Math.min(...L.map((q) => q.left)), r: Math.max(...L.map((q) => q.right)) };
    };
    const align = (e) => { const s = cs(e); let a = s.textAlign.replace(/^-(internal|webkit)-/, ""); return a === "center" ? "center" : "start"; };
    for (const h of document.querySelectorAll("h1,h2,h3")) {
      const p = h.nextElementSibling;
      if (!p || p.tagName !== "P" || !vis(h) || !vis(p) || h.closest("[aria-hidden=true],[data-lb-ignore]")) continue;
      const hs = cs(h), hr = h.getBoundingClientRect(), pr = p.getBoundingClientRect(), hl = firstLine(h), pl = firstLine(p);
      if (!hl || !pl) continue;
      const ha = align(h), pa = align(p), text = textOf(h);
      if (ha === "center" && pa === "center") { const d = Math.abs((hr.left + hr.right) / 2 - (pr.left + pr.right) / 2); if (d > 2) add("SUBLINE", "center-off", h, text, "paragraph centre is " + Math.round(d) + "px off the heading centre"); }
      else if (ha !== pa) add("SUBLINE", "align-mismatch", h, text, "heading is " + (ha === "center" ? "centered" : "start aligned") + ", paragraph is " + (pa === "center" ? "centered" : "start aligned"));
      else { const ltr = hs.direction !== "rtl", he = ltr ? hl.l : hl.r, pe = ltr ? pl.l : pl.r; if (Math.abs(he - pe) > 2) add("SUBLINE", "start-off", h, text, "heading starts at " + Math.round(he) + "px, paragraph at " + Math.round(pe) + "px"); }
      const par = h.parentElement, ps = cs(par);
      if (hs.display === "block" && /^(block|flow-root|list-item)$/.test(ps.display)) {
        const room = par.getBoundingClientRect().width - parseFloat(ps.paddingLeft) - parseFloat(ps.paddingRight) - parseFloat(ps.borderLeftWidth) - parseFloat(ps.borderRightWidth);
        if (hr.width < room - 4 && pr.width > hr.width + 2) add("SUBLINE", "wider", h, text, "paragraph is " + Math.round(pr.width) + "px wide, heading block " + Math.round(hr.width) + "px");
      }
    }
  });

  // THIN (1280px and wider): the main content spans under 55% of the viewport on a page with no sidebar that is not a reading page.
  run("THIN", () => {
    const cw = document.documentElement.clientWidth;
    if (cw < 1280) return;
    const host = document.querySelector("main") || document.body, skipChrome = host === document.body ? "header,nav,footer" : "";
    let l = Infinity, r = -Infinity;
    const take = (q) => { if (q.width > 0 && q.height > 0) { l = Math.min(l, q.left); r = Math.max(r, q.right); } };
    for (const { n, el } of TN) if (host.contains(el) && !(skipChrome && el.closest(skipChrome)) && !/fixed|sticky/.test(cs(el).position)) { const g = document.createRange(); g.selectNodeContents(n); [...g.getClientRects()].forEach(take); }
    for (const e of host.querySelectorAll("img,video,canvas,table,input,button,select,iframe,svg")) if (vis(e) && !(skipChrome && e.closest(skipChrome)) && e.getBoundingClientRect().width >= 40 && !e.closest("button,a,[aria-hidden=true]")) take(e.getBoundingClientRect());
    if (r <= l || TN.filter((x) => host.contains(x.el)).reduce((a, x) => a + x.t.length, 0) < 300) return; // a stub page has no content to measure
    const span = r - l;
    if (span >= cw * 0.55) return;
    const side = [...document.querySelectorAll("aside,[role=complementary],nav,body *")].some((e) => { // a tall narrow bar at a viewport edge
      const s = cs(e); if (!(e.tagName === "ASIDE" || e.getAttribute("role") === "complementary" || /fixed|sticky/.test(s.position))) return false;
      const q = e.getBoundingClientRect(); return vis(e) && q.height >= innerHeight * 0.6 && q.width <= cw * 0.35 && (q.left <= 8 || q.right >= cw - 8);
    });
    if (side) return;
    const long = [...document.querySelectorAll("p")].find((p) => vis(p) && textOf(p).length > 400);
    if (long) { const pr = document.createElement("div"); pr.style.cssText = "position:absolute;visibility:hidden;width:75ch;font:" + cs(long).font; long.parentElement.appendChild(pr); const ch = pr.getBoundingClientRect().width; pr.remove(); if (span <= ch + 64) return; }
    if (span <= 560 && document.querySelector("form input[type=password],form input[type=email]")) return; // a sign-in card
    add("THIN", "narrow", host, "", "content spans " + Math.round(span) + "px of " + cw + "px (" + Math.round((span / cw) * 100) + "%), under 55%");
  });

  // A11Y: contrast, touch targets, image alt, heading levels (the Tab focus ring check runs in web_balance.js).
  run("A11Y", () => {
    const cv = document.createElement("canvas"); cv.width = cv.height = 1;
    const cx = cv.getContext("2d", { willReadFrequently: true }), cc = new Map();
    const rgba = (str) => { if (cc.has(str)) return cc.get(str); cx.clearRect(0, 0, 1, 1); cx.fillStyle = "#000"; cx.fillStyle = str; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data, v = [d[0], d[1], d[2], d[3] / 255]; cc.set(str, v); return v; };
    const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
    const hex = (c) => "#" + c.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, "0")).join("");
    // Nearest opaque background, blending translucent layers. A gradient counts as its colour stops (the worst one decides); a url() image
    // on the way means "not computed". Returns the possible backgrounds, or null.
    const mix = (c, b) => b.map((v, k) => c[k] * c[3] + v * (1 - c[3]));
    const bgFor = (el) => {
      const layers = [];
      for (let a = el; a; a = a.parentElement) {
        const s = cs(a);
        if (s.backgroundImage !== "none") {
          if (/url\(/.test(s.backgroundImage)) return null;
          const stops = (s.backgroundImage.match(/(?:rgba?|hsla?|color|oklab|oklch|lab|lch)\([^)]*\)/g) || []).map(rgba);
          if (!stops.length) return null;
          layers.push({ stops });
          if (stops.every((c) => c[3] >= 0.999)) break;
        }
        const c = rgba(s.backgroundColor);
        if (c[3] > 0) { layers.push({ c }); if (c[3] >= 0.999) break; }
      }
      let bases = [[255, 255, 255]];
      for (let i = layers.length - 1; i >= 0; i--) {
        const l = layers[i];
        bases = l.c ? bases.map((b) => mix(l.c, b)) : bases.flatMap((b) => l.stops.map((c) => mix(c, b)));
        if (bases.length > 16) return null;
      }
      return bases;
    };
    const seen = new Map(); let checked = new Set();
    for (const { el } of TN) {
      if (checked.has(el)) continue; checked.add(el);
      if (el.closest(":disabled,[aria-disabled=true]")) continue;
      const r = el.getBoundingClientRect(), s = cs(el);
      if (r.width <= 2 || r.height <= 2 || /text/.test(s.webkitBackgroundClip || s.backgroundClip)) continue;
      const fg = rgba(s.webkitTextFillColor || s.color);
      let op = 1; for (let a = el; a && a !== document.documentElement; a = a.parentElement) op *= +cs(a).opacity;
      const a = fg[3] * op;
      if (a < 0.05) continue;
      const bgs = bgFor(el);
      if (!bgs) { warn.contrast++; continue; }
      let worst = null;
      for (const bg of bgs) {
        const col = fg.slice(0, 3).map((v, k) => v * a + bg[k] * (1 - a)), l1 = lum(col), l2 = lum(bg), ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
        if (!worst || ratio < worst.ratio) worst = { ratio, col, bg };
      }
      const size = parseFloat(s.fontSize), large = size >= 24 || (size >= 18.66 && parseInt(s.fontWeight) >= 700), need = large ? 3 : 4.5;
      if (worst.ratio >= need) continue;
      const key = hex(worst.col) + hex(worst.bg) + (large ? "L" : "S");
      const prev = seen.get(key);
      if (prev) { prev.n++; continue; }
      seen.set(key, { el, ratio: worst.ratio, need, col: worst.col, bg: worst.bg, size, n: 1 });
    }
    // A text that fails over something painted behind it that is not an ancestor (an absolutely positioned image or card): not computed.
    const behind = (el) => {
      el.scrollIntoView({ block: "center", behavior: "instant" });
      const q = el.getBoundingClientRect(), stack = document.elementsFromPoint((q.left + q.right) / 2, (q.top + q.bottom) / 2), i = stack.indexOf(el);
      return stack.slice(i + 1).some((e) => !e.contains(el) && !el.contains(e) && (/^(IMG|VIDEO|CANVAS|PICTURE|SVG)$/i.test(e.tagName) || cs(e).backgroundImage !== "none" || rgba(cs(e).backgroundColor)[3] > 0));
    };
    for (const v of seen.values()) {
      if (behind(v.el)) { warn.contrast++; continue; }
      add("A11Y", "contrast", v.el, textOf(v.el), v.ratio.toFixed(2) + ":1, needs " + v.need + ":1 (" + hex(v.col) + " on " + hex(v.bg) + ", " + Math.round(v.size) + "px" + (v.n > 1 ? ", " + v.n + " elements" : "") + ")");
    }
    scrollTo(0, 0);

    if (w <= 480) for (const el of document.querySelectorAll("a[href],button,input:not([type=hidden]),[role=button]")) {
      if (!vis(el) || el.closest("[aria-hidden=true],[data-lb-ignore]")) continue;
      let q = el.getBoundingClientRect();
      if (el.tagName === "INPUT" && /^(checkbox|radio)$/.test(el.type) && el.labels && el.labels[0] && vis(el.labels[0])) { const lq = el.labels[0].getBoundingClientRect(); q = { left: Math.min(q.left, lq.left), right: Math.max(q.right, lq.right), top: Math.min(q.top, lq.top), bottom: Math.max(q.bottom, lq.bottom), width: 0, height: 0 }; q.width = q.right - q.left; q.height = q.bottom - q.top; }
      if (q.right <= 0 || q.left >= innerWidth || q.width <= 2 || q.height <= 2) continue;
      if (el.tagName === "A" && cs(el).display === "inline" && el.parentElement && own(el.parentElement).length) continue; // a link inside running text
      if (q.width < 44 || q.height < 44) add("A11Y", "target", el, textOf(el) || el.getAttribute("aria-label") || el.value || "", Math.round(q.width) + "x" + Math.round(q.height) + "px, needs 44x44");
    }
    for (const i of document.querySelectorAll("img:not([alt])")) {
      const q = i.getBoundingClientRect();
      if (q.width > 1 && q.height > 1 && vis(i) && !/^(presentation|none)$/.test(i.getAttribute("role") || "")) add("A11Y", "img-alt", i, (i.getAttribute("src") || "").slice(-40), "img has no alt attribute (alt=\"\" is fine for decoration)");
    }
    let prev = 0;
    for (const h of document.querySelectorAll(HEADS)) {
      if (!vis(h) || h.closest("[aria-hidden=true],[hidden]")) continue;
      const lv = +h.tagName[1];
      if (prev && lv - prev > 1) add("A11Y", "heading-skip", h, textOf(h), "h" + prev + " then h" + lv);
      prev = lv;
    }
  });

  // BROKEN (in the page): images that failed to load. Links, console errors and page errors are read in web_balance.js.
  run("BROKEN", () => {
    for (const i of document.querySelectorAll("img")) if (i.complete && i.naturalWidth === 0 && i.currentSrc && !/\.svg(\?|#|$)/i.test(i.currentSrc) && !i.currentSrc.startsWith("data:")) add("BROKEN", "img", i, (i.getAttribute("src") || "").slice(-50), "image did not load (naturalWidth 0)");
  });

  // COVER: a fixed or sticky element on top of text or controls at scroll 0, and an anchor target left under a sticky header.
  run("COVER", () => {
    const fixedAll = [...document.querySelectorAll("body *")].filter((e) => { const p = cs(e).position; return (p === "fixed" || p === "sticky") && vis(e) && e.getBoundingClientRect().width >= 20 && e.getBoundingClientRect().height >= 20; });
    const fixedTop = fixedAll.filter((e) => !fixedAll.some((o) => o !== e && o.contains(e)));
    const modal = (e) => { try { if (e.matches(":modal")) return true; } catch {} return e.getAttribute("role") === "dialog" && e.getAttribute("aria-modal") === "true"; };
    const cands = [...document.querySelectorAll("a[href],button,input:not([type=hidden]),select,textarea,[role=button]," + HEADS + ",p,li,label,summary,figcaption,td,th,dt,dd,blockquote")].filter(vis);
    for (const F of fixedTop) {
      if (modal(F)) continue;
      const fr = F.getBoundingClientRect(); let n = 0;
      for (const c of cands) {
        if (n >= 3) break;
        if (F.contains(c) || c.contains(F) || fixedAll.some((o) => o !== F && o.contains(c))) continue;
        const rs = c.matches("a,button,input,select,textarea,[role=button]") ? [c.getBoundingClientRect()] : textRects(c).slice(0, 4);
        for (const q of rs) {
          const x = (q.left + q.right) / 2, y = (q.top + q.bottom) / 2;
          if (x < Math.max(0, fr.left) || x > Math.min(innerWidth, fr.right) || y < Math.max(0, fr.top) || y > Math.min(innerHeight, fr.bottom)) continue;
          const top = document.elementsFromPoint(x, y)[0];
          if (top && F.contains(top)) { add("COVER", "covers", F, textOf(c).slice(0, 40), cs(F).position + " element " + Math.round(fr.width) + "x" + Math.round(fr.height) + " covers " + seg(c) + " at scroll 0" + (F.getAttribute("role") === "dialog" ? " (role=dialog without aria-modal)" : "")); n++; break; }
        }
      }
    }
    // Anchor targets: scroll each into view and compare with the bottom of a bar stuck to the top.
    const ids = new Map();
    for (const a of document.querySelectorAll("a[href^='#']")) {
      const h = a.getAttribute("href"); if (h.length < 2 || /^#!?\//.test(h)) continue;
      let id = h.slice(1); try { id = decodeURIComponent(id); } catch {}
      const t = document.getElementById(id) || document.getElementsByName(id)[0];
      if (t && vis(t) && !ids.has(t)) ids.set(t, id);
      if (ids.size >= 15) break;
    }
    const bars = fixedAll.filter((e) => e.getBoundingClientRect().width >= document.documentElement.clientWidth * 0.5 && e.getBoundingClientRect().height < innerHeight * 0.5);
    for (const [t, id] of ids) {
      t.scrollIntoView({ block: "start", behavior: "instant" });
      const tq = t.getBoundingClientRect();
      const bar = bars.map((e) => ({ e, q: e.getBoundingClientRect() })).filter((b) => b.q.top <= 8 && b.q.bottom > 0).sort((a, b) => b.q.bottom - a.q.bottom)[0];
      if (bar && tq.top < bar.q.bottom - 1 && tq.top >= -1) add("COVER", "anchor-hidden", t, "#" + id, "target top is " + Math.round(tq.top) + "px, under the " + seg(bar.e) + " bar (" + Math.round(bar.q.bottom) + "px tall): add scroll-margin-top");
    }
    scrollTo(0, 0);
  });

  // RTL: under dir=rtl, direction arrows that are not mirrored, and text blocks forced to text-align: left or float: left.
  run("RTL", () => {
    const root = cs(document.documentElement).direction === "rtl" || cs(document.body).direction === "rtl" || document.querySelector("[dir=rtl]");
    if (!root) return;
    const DIR = /(^|[^a-z])(arrow|chevron|caret|next|prev|previous|back|forward)([^a-z]|$)/i, VERT = /(^|[^a-z])(up|down|top|bottom)([^a-z]|$)/i;
    const mirrored = (e) => {
      for (let a = e, i = 0; a && i < 4; a = a.parentElement, i++) {
        const s = cs(a), m = /^matrix(?:3d)?\(([^)]+)\)/.exec(s.transform);
        if (m && parseFloat(m[1].split(",")[0]) < 0) return true;
        if (/^-/.test(s.scale || "") || /^(180|-180)deg/.test(s.rotate || "")) return true;
      }
      return false;
    };
    for (const i of document.querySelectorAll("svg,img,i")) {
      if (cs(i).direction !== "rtl" || !vis(i)) continue;
      const use = i.querySelector && i.querySelector("use"), name = [typeof i.className === "string" ? i.className : i.className && i.className.baseVal, i.getAttribute("aria-label"), i.getAttribute("title"), i.getAttribute("alt"), i.getAttribute("data-icon"), i.id, use && (use.getAttribute("href") || use.getAttribute("xlink:href")), i.tagName === "IMG" ? (i.getAttribute("src") || "").split("/").pop() : ""].filter(Boolean).join(" ");
      if (DIR.test(name) && !VERT.test(name) && !mirrored(i)) add("RTL", "icon-not-mirrored", i, name.slice(0, 40), "direction icon in an RTL block has no negative x scale (transform: scaleX(-1) or rotate(180deg))");
    }
    for (const e of document.querySelectorAll("body *")) {
      if (!vis(e) || e.closest(SKIP)) continue;
      const s = cs(e);
      if (s.direction !== "rtl" || !(s.textAlign === "left" || s.float === "left")) continue;
      const t = own(e).map((n) => n.textContent).join(" ");
      if (/[\u0590-\u08ff]/.test(t || (/^(block|flex|grid|list-item|table-cell)$/.test(s.display) ? textOf(e) : ""))) add("RTL", s.float === "left" ? "float-left" : "text-align-left", e, t || textOf(e), (s.float === "left" ? "float: left" : "text-align: left") + " on RTL text, use start/inline-start");
    }
  });

  for (const k in over) { const [type, reason] = k.split("|"); hits.push({ type, reason, sel: "(page)", text: over[k] + " more", info: "capped at 25 per page and width" }); }
  const links = [...document.querySelectorAll("a[href]")].filter((a) => !a.closest("[data-lb-ignore]")).map((a) => ({ href: a.href, raw: a.getAttribute("href"), text: textOf(a).slice(0, 40) || a.getAttribute("aria-label") || "", sel: pathOf(a) }));
  return { hits, warn, links };
}

module.exports = { inspectPage };
