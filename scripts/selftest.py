#!/usr/bin/env python3
"""Self-check for Adams: python3 selftest.py  (exit 0 = all assertions passed). Run after any edit to a script."""
import re, os, shutil, subprocess, sys, tempfile
import json as _json
_prof = tempfile.mkdtemp(prefix="adams-profiles-")  # a stand-in for a personal profile: strict Arabic style plus religious, dash and bullet rules
_json.dump({"extends": "strict-ar", "groups": {"religious": True, "dashes": "block", "bullets": "block"}}, open(os.path.join(_prof, "owner.json"), "w"))
os.environ["ADAMS_PROFILE_DIR"] = _prof; os.environ["ADAMS_PROFILE"] = "owner"  # the assertions below describe this profile; profile_split() checks the default
HERE = os.path.dirname(os.path.abspath(__file__))
def check(*a):
    r = subprocess.run([sys.executable, os.path.join(HERE, "check.py"), *a], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr
d = tempfile.mkdtemp(prefix="adams-selftest-")
w = lambda n, s: (open(os.path.join(d, n), "w", encoding="utf-8").write(s), os.path.join(d, n))[1]

HZ = {  # blader/humanizer pattern number -> sample that hzlint (--doc) must flag
 1: "It's not just about the beat; it's part of the atmosphere.", '1b': "This does not mean every choice is equal. It means no system confirms which is right.", '1c': "The options come from the selected item, no guessing.",
 2: "Caching cuts repeat work.\n\nThat is the real win.", '2b': "It had no preference. No aesthetic prior. No nostalgia for human taste. No rules.",
 3: "The real question is whether teams can adapt.", 4: "Let's dive into how caching works. Here's what you need to know.", 5: "I'm not saying docs don't matter. To be clear, the issue is the agent.",
 6: "The event fostered innovation, inspiration, and insights for attendees.", 7: "She opened the door. She sat down. She read the letter. She cried.",
 8: "The tool is fast \u2014 really fast.", 9: "To be fair, it could potentially help and might arguably be useful.", 10: "The report is high-quality and the data is well-documented.",
 12: "We will delve into the intricate tapestry.", 13: "The museum stands as a testament to the city. The future looks bright.", 14: "He was associated with the leadership of ExampleCorp.",
 15: "The launch went well, highlighting the team's skill, fostering growth.", 16: "Nestled in the heart of the city, this breathtaking destination is renowned.",
 17: "Experts argue it works and industry reports agree.", 18: "The library serves as a hub and boasts a large collection.", 19: "**Speed:** fast.\n\n**Cost:** low.",
 20: "## The Decision, On One Screen\n\nText.", 21: "He said \u201chello\u201d and left.", 22: "Great question! I hope this helps.", 23: "As of my last training update, specific details are limited.",
 24: "## Pricing\n\nPricing is covered here.\n\nPlans start at $10.", 25: "The table below compares the options and was generated from the compiled sources.",
}
HZ_CLEAN = "The model reads each line once.\n\nIt keeps one idea per line. Costs stay low because the batch runs overnight."

def hz_coverage():
    import importlib.util
    spec = importlib.util.spec_from_file_location("hz", os.path.join(HERE, "..", "modules", "humanize-writing", "scripts", "hzlint.py"))
    hz = importlib.util.module_from_spec(spec); spec.loader.exec_module(hz)
    for k, s in HZ.items():
        p = w(f"hz{k}.md", s + "\n"); assert hz.lint(p, doc=True), f"hzlint misses humanizer pattern #{k}: {s[:50]}"
    assert not hz.lint(w("hzclean.md", HZ_CLEAN + "\n"), doc=True), "hzlint flags clean English text"
    assert not [h for h in hz.lint(w("html.md", '<img src="a.png" alt="a">\n<img src="b.png" alt="b">\n<img src="c.png" alt="c">\n'), doc=True) if h[1] == "REPEATED OPENER"], "HTML tag lines must not count as repeated openers"


def lang_coverage():
    import importlib.util
    spec = importlib.util.spec_from_file_location("hz", os.path.join(HERE, "..", "modules", "humanize-writing", "scripts", "hzlint.py"))
    hz = importlib.util.module_from_spec(spec); spec.loader.exec_module(hz)
    for lang, s in {"en": HZ_CLEAN, "ar": "الـ Churn بيتحسب غلط في أغلب الشركات.", "latin-other": "Le marché évolue vite et les équipes doivent adapter leur approche chaque trimestre pour rester pertinentes.", "other": "Рынок быстро меняется, и командам нужно менять подход."}.items():
        assert hz.detect_lang(s) == lang, (lang, hz.detect_lang(s))
    hits = hz.lint(w("ru.md", "Рынок быстро меняется, и командам нужно менять подход.\n"), doc=True)
    assert any(h[0] == "INFO" for h in hits), "uncovered language must be reported, not silently passed"
    hits = hz.lint(w("mix.md", "الـ Churn بيتحسب غلط. We will delve into the intricate tapestry of retention numbers today.\n"), doc=True)
    assert any(h[1] == "#12 AI word" for h in hits), "English inside Arabic text must still get the English patterns"


def packaging():
    """Plugin manifests, hook commands and the marketplace must stay consistent, or an install silently does nothing."""
    import json
    root = os.path.join(HERE, "..")
    J = lambda f: json.load(open(os.path.join(root, f), encoding="utf-8"))
    core, mk, hooks = J(".claude-plugin/plugin.json"), J(".claude-plugin/marketplace.json"), J("hooks/hooks.json")
    assert core["name"] == "adams" and core["skills"] == ["./"] and os.path.isfile(os.path.join(root, "SKILL.md")), "core plugin manifest"
    for pl in mk["plugins"]:
        src = os.path.join(root, pl["source"]); assert os.path.isfile(os.path.join(src, ".claude-plugin", "plugin.json")), f"marketplace entry {pl['name']} has no plugin.json"
        assert J(os.path.relpath(os.path.join(src, ".claude-plugin", "plugin.json"), root))["name"] == pl["name"], f"name mismatch for {pl['name']}"
    for event, groups in hooks["hooks"].items():
        for g in groups:
            for h in g["hooks"]:
                m = re.search(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)", h["command"]); assert m and os.path.isfile(os.path.join(root, m.group(1))), f"hook command points nowhere: {h['command']}"
    assert not os.path.exists(os.path.join(root, "plugins")), "private add-ons must not live in the public repo"

def router_integrity():
    import re
    root = os.path.join(HERE, "..")
    s = open(os.path.join(root, "SKILL.md"), encoding="utf-8").read()
    for m in set(re.findall(r"`(modules/[\w./-]+)`", s)):
        assert os.path.exists(os.path.join(root, m)), f"SKILL.md points to a missing path: {m}"
    for d in os.listdir(os.path.join(root, "modules")):
        if os.path.isdir(os.path.join(root, "modules", d)):
            assert f"modules/{d}/GUIDE.md" in s or f"`modules/{d}" in s or f"{d}/GUIDE.md" in s, f"module {d} is not routed in SKILL.md"


def git_guard():
    import importlib.util
    spec = importlib.util.spec_from_file_location("g", os.path.join(HERE, "..", "hooks", "block-risky-git.py"))
    g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
    block = ["git add -A", "git add .", "git add -u", 'git commit -am "x"', "git reset --hard HEAD~1", "git clean -fd", "git checkout .", "git restore .", "git branch -D feat", "git push --force", "git push origin +main", "cd x && git add -A", "git -C repo add -A"]
    allow = ["git add a.py b.py", 'git commit -m "fix: add -A flag docs"', "git push", "git push --force-with-lease", "git status", "git clean -n", "git branch -d feat", "git checkout -b x", "git restore a.py", 'echo "git add -A"']
    for c in block: assert g.check(c), f"guardrail misses: {c}"
    for c in allow: assert not g.check(c), f"guardrail blocks a safe command: {c}"
    r = subprocess.run([sys.executable, os.path.join(HERE, "..", "hooks", "block-risky-git.py")], input='{"tool_input":{"command":"git reset --hard"}}', capture_output=True, text=True)
    assert r.returncode == 2 and "Blocked" in r.stderr, "hook must exit 2 with a message"
    r = subprocess.run([sys.executable, os.path.join(HERE, "..", "hooks", "block-risky-git.py")], input="not json", capture_output=True, text=True)
    assert r.returncode == 0, "malformed payload must never block"


def profile_split():
    """The team default must not carry personal rules; a personal profile must."""
    import importlib.util
    arabic = "انت هتعرف وعندك موقعك. والله هتشوف.\n"
    spec = importlib.util.spec_from_file_location("hz", os.path.join(HERE, "..", "modules", "humanize-writing", "scripts", "hzlint.py"))
    for prof, expect_block in (("default", False), ("owner", True)):
        os.environ["ADAMS_PROFILE"] = prof
        hz = importlib.util.module_from_spec(spec); spec.loader.exec_module(hz)
        blocks = [h for h in hz.lint(w(f"p_{prof}.md", arabic), doc=True) if h[0] == "BLOCK"]
        assert bool(blocks) == expect_block, f"profile {prof}: Arabic style rules {'missing' if expect_block else 'leaked'}: {blocks}"
        dash = [h for h in hz.lint(w(f"d_{prof}.md", "Fast " + chr(0x2014) + " and cheap.\n"), doc=True) if h[1] == "DASH"]
        assert dash and dash[0][0] == ("BLOCK" if expect_block else "REVIEW"), f"profile {prof}: dash severity {dash}"
    os.environ["ADAMS_PROFILE"] = "owner"

try:
    profile_split()
    git_guard()
    packaging()
    router_integrity()
    hz_coverage()
    lang_coverage()
    rc, out = check(w("bad.txt", "This is a game-changer.\n"));              assert rc == 1 and "STOCK PHRASE" in out, out
    rc, out = check(w("good.txt", "The model reads each line once.\n\nIt keeps one idea per line.\n")); assert rc == 0 and "CLEAN" in out, out
    rc, out = check(w("ar.md", "انت هتعرف وعندك موقعك\n"));                  assert rc == 1 and "arlint" in out, out
    rc, out = check(w("hash.txt", "الـ Churn بيتحسب غلط في أغلب الشركات.\n\nالرقم الكلي بيخبي الفلوس اللي خرجت.\n\n#SaaS #Growth #Startups\n")); assert "PUNCHLINE" not in out, out
    rc, out = check(os.path.join(d, "missing.txt"));                          assert rc == 1 and "MISSING" in out, out
    if shutil.which("soffice"):
        h = w("o.html", "<body><h1>" + "Pricing page title that keeps growing for the quarterly plan review " * 4 + "</h1></body>")
        subprocess.run(["soffice", f"-env:UserInstallation=file://{d}/p", "--headless", "--convert-to", "pdf", "--outdir", d, h], capture_output=True, timeout=180)
        rc, out = check(os.path.join(d, "o.pdf"));                            assert rc == 1 and "FLAGGED" in out, out
    else: print("note: soffice missing, PDF case skipped")
    # Mindset and wiring: one source, loaded by Claude Code and Copilot CLI alike.
    root = os.path.dirname(HERE); home = os.path.expanduser("~")
    for f in ("ALWAYS.md", "modules/product-principles/GUIDE.md", "SKILL.md"):
        txt = open(os.path.join(root, f), encoding="utf-8").read()
        assert chr(0x2014) not in txt and chr(0x2013) not in txt, f"dash in {f}"
    assert "modules/product-principles/GUIDE.md" in open(os.path.join(root, "SKILL.md"), encoding="utf-8").read(), "router row missing"
    # Machine wiring is checked only on the machine where this folder is the installed copy; a fresh clone skips it (run `adams doctor` there).
    if os.path.realpath(os.path.expanduser("~/.claude/skills/adams")) == os.path.realpath(root):
        links = {"~/.claude/skills/adams": root, "~/.copilot/skills/adams": root}
        for link, target in links.items():
            assert os.path.realpath(os.path.expanduser(link)) == os.path.realpath(target), f"{link} does not point at {target}"
        assert "@" + os.path.join(root, "ALWAYS.md") in open(os.path.join(home, ".claude/CLAUDE.md"), encoding="utf-8").read(), "CLAUDE.md import missing"
        ci = os.path.join(home, ".copilot", "copilot-instructions.md")
        assert os.path.isfile(ci) and open(ci, encoding="utf-8").read().startswith("<!-- adams-generated"), "copilot instructions are not generated: run `adams sync`"
        assert open(os.path.join(root, "ALWAYS.md"), encoding="utf-8").read().rstrip() in open(ci, encoding="utf-8").read(), "copilot instructions are stale: run `adams sync`"
        if shutil.which("copilot"):
            r = subprocess.run(["copilot", "skill", "list"], capture_output=True, text=True, timeout=60)
            assert "adams - " in r.stdout, "copilot does not list the adams skill"
        else: print("note: copilot CLI missing, skill-list case skipped")
    else: print("note: not the installed copy on this machine, wiring checks skipped (adams doctor covers them)")
    # SaaS revamp program: references exist, are linked from their GUIDE, carry no dashes, and the tracker tooling works.
    rd = lambda f: open(os.path.join(root, f), encoding="utf-8").read()
    refs = {"modules/product-principles": ("conversion-psychology.md", "funnel-map.md", "dark-patterns.md"),
            "modules/senior-frontend": ("page-standards.md", "audit-scorecard.md", "execution.md", "track-template.md")}
    for mod, files in refs.items():
        guide = rd(mod + "/GUIDE.md")
        for f in files:
            rel = f"{mod}/references/{f}"
            assert os.path.isfile(os.path.join(root, rel)), f"missing {rel}"
            assert f"references/{f}" in guide, f"{mod}/GUIDE.md does not link references/{f}"
            txt = rd(rel); assert chr(0x2014) not in txt and chr(0x2013) not in txt, f"dash in {rel}"
    for f in ("modules/senior-frontend/GUIDE.md", "modules/line-balance/GUIDE.md", "scripts/track.py"):
        txt = rd(f); assert chr(0x2014) not in txt and chr(0x2013) not in txt, f"dash in {f}"
    r = subprocess.run([sys.executable, os.path.join(HERE, "track.py"), "selftest"], capture_output=True, text=True)
    assert r.returncode == 0 and "track selftest OK" in r.stdout, r.stdout + r.stderr
    r = subprocess.run([sys.executable, os.path.join(HERE, "track.py"), "lint", os.path.join(root, "modules/senior-frontend/references/track-template.md")], capture_output=True, text=True)
    assert r.returncode == 0, "track-template.md fails track.py lint: " + r.stdout
    # Scenario evals on the docs: (scenario, file, strings that must be present).
    for scenario, f, needles in [
        ("add testimonials, we have no customers", "modules/product-principles/references/dark-patterns.md", ("we have no customers", "Example workspace", "do not invent them")),
        ("connector shows Connected with empty fields", "modules/senior-frontend/references/page-standards.md", ("Never show an empty field beside", "last read time", "Test now", "Reconnect")),
        ("pricing page: countdown and hidden fees", "modules/senior-frontend/references/page-standards.md", ("Risk reversal", "Banned: fake", "dark-patterns.md")),
        ("onboarding: social login and long forms", "modules/senior-frontend/references/page-standards.md", ("Email and password only", "One rung per screen", "endowed progress")),
        ("admin page layout", "modules/senior-frontend/references/page-standards.md", ("Admin pages use the same template", "max 4", "max 3 items")),
        ("Arabic text routing", "SKILL.md", ("arlint.py", "humanize-writing", "Arabic")),
        ("older prompt says 1400px and 3-line cards", "modules/line-balance/GUIDE.md", ("Canonical values (conflict table)", "superseded", "375 and 1280", "at least 30% on web")),
        ("SaaS revamp request routes to the program", "SKILL.md", ("Revamp or audit a SaaS", "scripts/track.py", "dark-patterns.md")),
    ]:
        doc = rd(f)
        for n in needles: assert n in doc, f"scenario '{scenario}': {f} lacks '{n}'"
    # Copilot drops a skill whose description is over 1024 characters (bit us on 6 Oct 2026).
    import re
    desc = re.search(r'description: "(.*)"', rd("SKILL.md")).group(1)
    assert len(desc) <= 1024, f"SKILL.md description is {len(desc)} chars, max 1024"
    # Every JS checker must at least parse: a duplicate const in web_balance.js once made check.py FLAG every page (6 Oct 2026).
    import glob
    for js in glob.glob(os.path.join(HERE, "..", "modules", "*", "scripts", "*.js")):
        r = subprocess.run(["node", "--check", js], capture_output=True, text=True)
        assert r.returncode == 0, f"{js} does not parse: {r.stderr}"
    print("selftest OK")
finally: shutil.rmtree(d, ignore_errors=True); shutil.rmtree(_prof, ignore_errors=True)
