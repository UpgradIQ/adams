#!/usr/bin/env python3
"""Pre-render wrap simulator for generated decks.
Input: JSON list of text boxes logged from the generator, each
{slide, text (string or pptxgenjs runs), w (inches), fs (pt), bold, cs (charSpacing pt)}.
Usage: python3 wrap_sim.py textlog.json [MIN_RATIO] [ALL]
Uses Liberation Sans (Arial metrics). Final proof is still line_balance.py on the rendered PDF."""
import json, os, sys
if any(a in ('-h', '--help') for a in sys.argv[1:]):
    print(__doc__); sys.exit(0)
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
ImageFont = _need("PIL.ImageFont", "pillow>=10,<13")
# Arial metrics: Liberation Sans on Linux, Arial on macOS or Windows
FONTS = [("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
         ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
         ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf")]
R, B = next((f for f in FONTS if os.path.exists(f[0]) and os.path.exists(f[1])), (None, None))
if not R: sys.exit("No Arial-metric font found (Liberation Sans or Arial). Install one, then run again.")
LOG = sys.argv[1] if len(sys.argv) > 1 else "textlog.json"
MIN = float(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] != "ALL" else 0.5
cache = {}
def font(bold, size):
    k = (bold, size)
    if k not in cache: cache[k] = ImageFont.truetype(B if bold else R, int(size * 20))
    return cache[k]
def width(t, bold, size, cs):
    return font(bold, size).getlength(t) / 20 + cs * len(t)  # points
def wrap(text, wpt, bold, size, cs):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if width(t, bold, size, cs) <= wpt or not cur: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines
bad = 0
for e in json.load(open(LOG)):
    paras = []
    if isinstance(e["text"], str): paras.append((e["text"], e["bold"], 0))
    else:
        buf, bold, ind = "", e["bold"], 0
        for r in e["text"]:
            o = r.get("options", {})
            buf += r["text"]; bold = o.get("bold", e["bold"]) if not buf.strip() == r["text"].strip() else o.get("bold", e["bold"])
            if o.get("bullet"): ind = o["bullet"].get("indent", 27) if isinstance(o["bullet"], dict) else 27
            if o.get("breakLine"): paras.append((buf, e["bold"], ind)); buf = ""; ind = 0
        if buf: paras.append((buf, e["bold"], ind))
    for p, bold, ind in paras:
        wpt = e["w"] * 72 - ind
        ls = wrap(p, wpt, bold, e["fs"], e["cs"])
        if len(ls) < 2: continue
        last = width(ls[-1], bold, e["fs"], e["cs"]) / wpt
        flag = len(ls[-1].split()) == 1 or last < MIN or ind > 0
        if "ALL" in sys.argv and len(ls)>1: print(f"   S{e['slide']} n={len(ls)} last={last:.0%} {p[:40]}")
        if flag:
            bad += 1
            print(f"S{e['slide']:>2} w={e['w']} lines={len(ls)} last={last:.0%} | {p[:70]}  ->  ...{ls[-1]!r}")
print("FLAGGED", bad)
