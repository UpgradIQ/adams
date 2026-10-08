#!/usr/bin/env python3
"""adams tokens: estimated token cost (chars/4) of what Adams loads. An estimate, not the exact count."""
import glob, os, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PERSONAL = os.path.expanduser("~/.config/adams/personal.md")
def est(n): return n // 4
def size(path): return os.path.getsize(path) if os.path.isfile(path) else 0
def tree(d): return sum(size(f) for f in glob.glob(os.path.join(d, "**", "*"), recursive=True))

def main():
    reminder = len(subprocess.run(["sh", os.path.join(ROOT, "hooks", "adams_reminder.sh")], capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout)
    always, personal, skill = size(os.path.join(ROOT, "ALWAYS.md")), size(PERSONAL), size(os.path.join(ROOT, "SKILL.md"))
    rows = [("ALWAYS.md (every session)", always), ("personal.md (every session)", personal), ("reminder hook (once per session)", reminder), ("SKILL.md (on invoke)", skill)]
    guides = {}
    for g in sorted(glob.glob(os.path.join(ROOT, "modules", "*", "GUIDE.md"))):
        m = os.path.basename(os.path.dirname(g)); guides[m] = size(g)
        rows.append((f"modules/{m}/GUIDE.md", size(g)))
        r = tree(os.path.join(os.path.dirname(g), "references"))
        if r: rows.append((f"modules/{m}/references (total)", r))
    print("Estimated tokens (chars / 4; `claude plugin details adams@adams` gives the exact count)")
    for name, n in rows: print(f"{est(n):>7}  {name}")
    print(f"{est(always + personal + reminder):>7}  PER-SESSION BASELINE (ALWAYS + personal + reminder once)")
    typical = skill + sum(guides.get(m, 0) for m in ("product-principles", "workflow", "humanize-writing"))
    print(f"{est(typical):>7}  TYPICAL TEXT TASK (SKILL + product-principles + workflow + humanize-writing)")

if __name__ == "__main__": main()
