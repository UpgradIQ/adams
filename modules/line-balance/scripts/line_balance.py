#!/usr/bin/env python3
"""Line balance check on a rendered PDF.
Usage: python3 line_balance.py file.pdf [--min 0.5] [--pages 1-5]
Flags: a paragraph whose last line is one word, or shorter than MIN of the
paragraph's widest line; wrapped bullet items; and rows of side-by-side blocks
with unequal line counts."""
import sys, argparse
def _need(mod, pkg):
    """Import a module, installing its package once with pip if it is missing (free, local)."""
    import importlib, subprocess
    try: return importlib.import_module(mod)
    except ImportError: pass
    import os
    if os.environ.get("ADAMS_AUTO_INSTALL") == "0": sys.exit(f"missing Python package; install it yourself: python3 -m pip install --user '{pkg}' (auto-install is off: ADAMS_AUTO_INSTALL=0)")
    print(f"[setup] {pkg} not found, installing it once ...", file=sys.stderr)
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    base = [sys.executable, "-m", "pip", "install", "--quiet", pkg] + ([] if in_venv else ["--user"])
    if subprocess.call(base) != 0: subprocess.check_call(base + ["--break-system-packages"])
    importlib.invalidate_caches()
    if not in_venv:
        import site; sys.path.insert(0, site.getusersitepackages())
    return importlib.import_module(mod)
pdfplumber = _need("pdfplumber", "pdfplumber>=0.11,<0.12")
from collections import defaultdict

ap = argparse.ArgumentParser()
ap.add_argument("pdf"); ap.add_argument("--min", type=float, default=0.5)
ap.add_argument("--pages", default=None)
a = ap.parse_args()

def page_range(spec, n):
    if not spec: return range(n)
    lo, _, hi = spec.partition("-"); return range(int(lo) - 1, int(hi or lo))

BULLETS = {"•", "·", "-", "–", "◦", "▪", "*"}
bad = 0
with pdfplumber.open(a.pdf) as pdf:
    for pi in page_range(a.pages, len(pdf.pages)):
        words = pdf.pages[pi].extract_words(keep_blank_chars=False, use_text_flow=True, extra_attrs=["size"])
        # 1) words -> lines (same baseline, same size, horizontally contiguous)
        lines = []
        for w in sorted(words, key=lambda w: (round(w["bottom"]), w["x0"])):
            for L in lines:
                if abs(L["bottom"] - w["bottom"]) < 1.5 and abs(L["size"] - w["size"]) < 0.3 \
                        and 0 <= w["x0"] - L["x1"] < w["size"] * 1.2:
                    L["x1"] = w["x1"]; L["words"].append(w["text"])
                    if len(L["words"]) == 2 and L["words"][0] in BULLETS: L["tx0"] = w["x0"]
                    break
            else:
                lines.append({"x0": w["x0"], "x1": w["x1"], "top": w["top"], "bottom": w["bottom"],
                              "size": w["size"], "words": [w["text"]], "tx0": w["x0"]})
        # 2) lines -> paragraphs (same size, shared left OR right edge, tight leading)
        lines.sort(key=lambda L: (L["top"], L["x0"]))
        paras = []
        for L in lines:
            if L["words"][0] in BULLETS: paras.append([L]); continue  # each bullet item is its own paragraph
            for P in paras:
                q = P[-1]
                gap = L["top"] - q["bottom"]
                edge = abs(L["x0"] - q["tx0"]) < 2 or abs(L["x0"] - q["x0"]) < 2 or abs(L["x1"] - q["x1"]) < 2
                if abs(L["size"] - q["size"]) < 0.3 and edge and -1 < gap < L["size"] * 0.9:
                    P.append(L); break
            else:
                paras.append([L])
        # 3) orphan / short last line / wrapped bullet
        for P in paras:
            if len(P) < 2: continue
            full = max(l["x1"] - l["x0"] for l in P[:-1])
            if P[0]["words"][0] in BULLETS:
                bad += 1; print(f"p{pi+1} WRAPPED_BULLET '{' '.join(P[0]['words'])[:50]}' ({len(P)} lines, keep list items on one line)")
                continue
            last = P[-1]; ratio = (last["x1"] - last["x0"]) / full
            if len(last["words"]) == 1 or ratio < a.min:
                bad += 1
                print(f"p{pi+1} ORPHAN last={ratio:.0%} '{' '.join(P[0]['words'])[:50]}' -> '{' '.join(last['words'])}'")
        # 4) symmetry: blocks starting on the same top with the same font size should match line counts
        rows = defaultdict(list)
        for P in paras:
            rows[(round(P[0]["top"] / 3), round(P[0]["size"], 1))].append(P)
        for (t, sz), ps in rows.items():
            if len(ps) < 3: continue  # need 3+ siblings to call it a row of cards
            counts = sorted({len(p) for p in ps})
            if len(counts) > 1:
                bad += 1
                print(f"p{pi+1} UNEVEN row size={sz} line counts {[len(p) for p in sorted(ps, key=lambda p: p[0]['x0'])]}")
print("FLAGGED", bad)
sys.exit(1 if bad else 0)
