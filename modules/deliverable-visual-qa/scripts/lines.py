"""Broken-line check, kept for old commands. Forwards to the single source of truth:
line-balance/scripts/line_balance.py (handles LTR and RTL, so the old 'rtl' flag is ignored).
Usage: python3 lines.py file.pdf [rtl] [--min 0.5] [--pages 3-7]"""
import os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
target = os.path.join(here, "..", "..", "line-balance", "scripts", "line_balance.py")
args = [a for a in sys.argv[1:] if a != "rtl"]
sys.exit(subprocess.call([sys.executable, target] + args))
