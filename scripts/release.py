#!/usr/bin/env python3
"""Cut a release: python3 scripts/release.py X.Y.Z
Moves the "Unreleased" changelog notes under the new version, bumps VERSION and the plugin manifest, runs the selftest,
commits "Release X.Y.Z" and tags vX.Y.Z. It does not push: review, then `git push origin main --follow-tags`.
Pushing the tag publishes the GitHub Release (see .github/workflows/release.yml)."""
import datetime, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sh = lambda *a: subprocess.run(a, cwd=ROOT, capture_output=True, text=True)
sv = lambda v: tuple(map(int, v.split(".")))

def main(new):
    if not re.fullmatch(r"\d+\.\d+\.\d+", new or ""): sys.exit(__doc__)
    old = open(os.path.join(ROOT, "VERSION")).read().strip()
    if sv(new) <= sv(old): sys.exit(f"{new} must be newer than {old}")
    if sh("git", "status", "--porcelain", "--untracked-files=no").stdout.strip(): sys.exit("Commit or stash your changes first.")
    cl = os.path.join(ROOT, "CHANGELOG.md"); text = open(cl, encoding="utf-8").read()
    m = re.search(r"^## Unreleased\n(.*?)(?=^## )", text, re.S | re.M)
    if not m or not m.group(1).strip(): sys.exit('CHANGELOG.md has no notes under "## Unreleased".')
    text = text.replace("## Unreleased\n", f"## Unreleased\n\n## {new} ({datetime.date.today().isoformat()})\n", 1)
    open(cl, "w", encoding="utf-8").write(text)
    open(os.path.join(ROOT, "VERSION"), "w").write(new + "\n")
    pj = os.path.join(ROOT, ".claude-plugin", "plugin.json"); d = json.load(open(pj)); d["version"] = new
    json.dump(d, open(pj, "w"), indent=2); open(pj, "a").write("\n")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "selftest.py")], capture_output=True, text=True)
    if "selftest OK" not in r.stdout: sh("git", "checkout", "--", "."); sys.exit("selftest failed, release reverted:\n" + r.stdout[-800:] + r.stderr[-800:])
    sh("git", "add", "VERSION", "CHANGELOG.md", ".claude-plugin/plugin.json")
    if sh("git", "commit", "-m", f"Release {new}").returncode: sys.exit("commit failed")
    sh("git", "tag", "-a", f"v{new}", "-m", f"Adams {new}")  # annotated, so `git push --follow-tags` sends it; print(f"Released {old} -> {new} locally. Publish: git push origin main --follow-tags")

if __name__ == "__main__": main(sys.argv[1] if len(sys.argv) > 1 else "")
