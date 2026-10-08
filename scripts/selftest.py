#!/usr/bin/env python3
"""Self-check for Adams: python3 selftest.py  (exit 0 = all assertions passed). Run after any edit to a script."""
import hashlib, re, os, shutil, subprocess, sys, tempfile, time
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

HZ = {  # English-tell pattern number -> sample that hzlint (--doc) must flag
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
        p = w(f"hz{k}.md", s + "\n"); assert hz.lint(p, doc=True), f"hzlint misses English-tell pattern #{k}: {s[:50]}"
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


def versioning():
    import json
    root = os.path.join(HERE, "..")
    ver = open(os.path.join(root, "VERSION"), encoding="utf-8").read().strip()
    assert re.fullmatch(r"\d+\.\d+\.\d+", ver), f"VERSION is not semver: {ver}"
    assert json.load(open(os.path.join(root, ".claude-plugin", "plugin.json")))["version"] == ver, "VERSION and plugin.json disagree"
    cl = open(os.path.join(root, "CHANGELOG.md"), encoding="utf-8").read()
    assert re.search(rf"^## {re.escape(ver)}\b", cl, re.M) or "## Unreleased" in cl, "CHANGELOG has neither this version nor an Unreleased section"

def update_flow():
    """A clone follows release tags: report, update when clean, skip when dirty, throttle the daily check, honour the opt-out."""
    t = tempfile.mkdtemp(prefix="adams-upd-")
    env = {**os.environ, "HOME": t + "/home", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    env.pop("ADAMS_AUTO_UPDATE", None)
    G = lambda cwd, *a: subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, env=env)
    U = lambda cwd, *a, **e: subprocess.run([sys.executable, os.path.join(cwd, "scripts", "update.py"), *a], capture_output=True, text=True, env={**env, **e})
    try:
        src = os.path.join(t, "src"); os.makedirs(os.path.join(src, "bin")); os.makedirs(os.path.join(src, "scripts"))
        for f in ("bin/adams", "scripts/update.py"): shutil.copy(os.path.join(HERE, "..", f), os.path.join(src, f))
        def release(ver, notes):
            open(os.path.join(src, "VERSION"), "w").write(ver + "\n")
            old = open(os.path.join(src, "CHANGELOG.md")).read() if os.path.exists(os.path.join(src, "CHANGELOG.md")) else ""
            open(os.path.join(src, "CHANGELOG.md"), "w").write(f"## {ver}\n{notes}\n\n" + old)
            G(src, "add", "-A"); G(src, "commit", "-qm", ver); G(src, "tag", "v" + ver)
        G(src, "init", "-q", "-b", "main"); release("1.0.0", "- first")
        clone = os.path.join(t, "clone"); G(t, "clone", "-q", src, clone)
        release("1.1.0", "- brand new thing")
        r = U(clone, "update", "--check"); assert "1.1.0 is available" in r.stdout, r.stdout + r.stderr
        r = U(clone, "update", "--auto"); assert "updated 1.0.0 -> 1.1.0" in r.stdout and "brand new thing" in r.stdout, r.stdout + r.stderr
        assert open(os.path.join(clone, "VERSION")).read().strip() == "1.1.0"
        release("1.2.0", "- later")
        assert U(clone, "update", "--auto").stdout == "", "the daily check must be throttled"
        open(os.path.join(clone, "CHANGELOG.md"), "a").write("local edit\n")
        r = U(clone, "update"); assert "uncommitted changes" in r.stdout and open(os.path.join(clone, "VERSION")).read().strip() == "1.1.0", r.stdout
        G(clone, "checkout", "--", "."); os.remove(os.path.join(t, "home", ".config", "adams", "update-check.json"))
        assert U(clone, "update", "--auto", ADAMS_AUTO_UPDATE="0").stdout == "" and open(os.path.join(clone, "VERSION")).read().strip() == "1.1.0", "opt-out must stop the update"
        r = U(clone, "update"); assert "updated 1.1.0 -> 1.2.0" in r.stdout, r.stdout
        shutil.rmtree(os.path.join(clone, ".git")); assert "plugin" in U(clone, "update").stdout, "a non-git install must point to the plugin manager"
    finally: shutil.rmtree(t, ignore_errors=True)

# Adams stands alone: no tracked file except NOTICE (which carries the license notices) names another skill, plugin or third-party project.
DENY = re.compile(r"find-skills|impeccable|frontend-design|high-end-visual|ui-ux-pro|copywriting|marketing-psychology|linkedin-writer|kpi-dashboard|dataviz|nextjs-best-practices|react-best-practices|supabase-postgres-best|web-perf|brainstorming|writing-plans|\btdd\b|verification-quality|design-review|motion-designer|programmatic-seo|seo-audit|ai-seo|cold-email|ponytail|superpowers|mattpocock|pocock|skills\.sh|blader|humanizer|vercel-labs|anthropics/skills|companion skills?|adapted from|merged from", re.I)

def standalone():
    files = subprocess.run(["git", "ls-files"], cwd=os.path.dirname(HERE), capture_output=True, text=True).stdout.split()
    assert files, "git ls-files returned nothing"
    for f in files:
        if f in ("NOTICE", "scripts/selftest.py"): continue  # NOTICE is the one place for third-party notices; selftest.py holds the deny list
        try: txt = open(os.path.join(os.path.dirname(HERE), f), encoding="utf-8").read()
        except (UnicodeDecodeError, OSError): continue
        m = DENY.search(txt); assert not m, f"{f} names a third party ({m.group(0)}); only NOTICE may"

def authorship():
    """Commits in this repository are authored by the maintainer; the release script must not add a co-author trailer."""
    assert "Co-Authored-By" not in open(os.path.join(HERE, "release.py"), encoding="utf-8").read(), "release.py must not add a co-author trailer"

def reminder_text():
    txt = open(os.path.join(HERE, "..", "hooks", "adams_reminder.sh"), encoding="utf-8").read()
    assert "adams:adams" in txt, "the reminder must name the plugin form of the skill"
    assert " his " not in txt and "him" not in txt.split(), "the reminder must use neutral wording"
    assert "Align first" in txt and "recommended" in txt, "the reminder must carry the auto-ask rule"
    root = os.path.join(HERE, "..")
    assert "asks first" in open(os.path.join(root, "ALWAYS.md"), encoding="utf-8").read(), "ALWAYS.md must carry the auto-ask rule"
    assert "## 1. Align" in open(os.path.join(root, "modules", "workflow", "GUIDE.md"), encoding="utf-8").read(), "workflow guide must hold the align loop"

def plugin_guard():
    """With the plugin enabled, `adams install` must not add a second copy of the skill link or the hooks."""
    t = tempfile.mkdtemp(prefix="adams-plug-")
    env = {**os.environ, "HOME": t}
    os.makedirs(os.path.join(t, ".claude"))
    _json.dump({"enabledPlugins": {"adams@adams": True}}, open(os.path.join(t, ".claude", "settings.json"), "w"))
    A = lambda *a: subprocess.run([sys.executable, os.path.join(HERE, "..", "bin", "adams"), *a], capture_output=True, text=True, env=env)
    try:
        r = A("install"); assert r.returncode == 0 and "plugin" in r.stdout, r.stdout + r.stderr
        assert not os.path.lexists(os.path.join(t, ".claude", "skills", "adams")), "plugin installs must not also link the skill"
        assert "hooks" not in _json.load(open(os.path.join(t, ".claude", "settings.json"))), "plugin installs must not also register the hooks"
        assert os.path.islink(os.path.join(t, ".local", "bin", "adams")), "the adams command is still linked"
        r = A("install", "--link"); assert r.returncode == 0 and os.path.islink(os.path.join(t, ".claude", "skills", "adams")), "install --link must link the skill even with the plugin enabled: " + r.stdout + r.stderr
        d = A("doctor").stdout; assert "Claude Code skill (plugin enabled, or link)" in d and "MISSING" not in d.split("optional")[0], d
    finally: shutil.rmtree(t, ignore_errors=True)

def project_tools():
    """adams init writes the project profile; check --since and --changed look only at what changed."""
    t = tempfile.mkdtemp(prefix="adams-proj-")
    env = {**os.environ, "HOME": t + "/home", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    A = lambda *a: subprocess.run([sys.executable, os.path.join(HERE, "..", "bin", "adams"), *a], cwd=t, capture_output=True, text=True, env=env)
    G = lambda *a: subprocess.run(["git", *a], cwd=t, capture_output=True, text=True, env=env)
    try:
        r = A("init", "--profile", "strict-ar"); assert r.returncode == 0 and _json.load(open(os.path.join(t, ".adams", "config.json")))["profile"] == "strict-ar", r.stdout
        assert A("init").returncode == 1, "init must not overwrite without --force"
        assert A("init", "--profile", "nope").returncode == 2
        os.remove(os.path.join(t, ".adams", "config.json")); os.rmdir(os.path.join(t, ".adams"))
        G("init", "-q", "-b", "main"); open(os.path.join(t, "a.md"), "w").write("The model reads each line once.\n\nIt keeps one idea per line.\n"); G("add", "a.md"); G("commit", "-qm", "a")
        r = A("check", "--changed"); assert r.returncode == 0 and "no changed" in r.stdout, r.stdout
        open(os.path.join(t, "b.md"), "w").write("This is a game-changer.\n")
        r = A("check", "--changed"); assert r.returncode == 1 and "b.md" in r.stdout and "a.md" not in r.stdout.replace("b.md", ""), r.stdout
        G("add", "b.md"); G("commit", "-qm", "b")
        r = A("check", "--since", "HEAD~1"); assert r.returncode == 1 and "b.md" in r.stdout, r.stdout
    finally: shutil.rmtree(t, ignore_errors=True)

def corpus_and_audit():
    """Humanize regression corpus (stock-AI samples must be flagged, plain human samples must not) and the AI-search audit on a tiny folder."""
    import importlib.util
    root = os.path.join(HERE, "..")
    cdir = os.path.join(root, "modules", "humanize-writing", "tests", "corpus")
    spec = importlib.util.spec_from_file_location("hz", os.path.join(root, "modules", "humanize-writing", "scripts", "hzlint.py"))
    hz = importlib.util.module_from_spec(spec); spec.loader.exec_module(hz)
    rd = lambda n: open(os.path.join(cdir, n), encoding="utf-8").read()
    for n in ("ai_en", "ai_ar", "human_en", "human_ar"):
        t = rd(n + ".txt"); assert chr(0x2014) not in t and chr(0x2013) not in t, f"dash in corpus {n}"
        if n.endswith("_ar"): assert all(re.match(r"[\u0621-\u064A]", l) for l in t.splitlines() if l.strip()), f"{n}: every Arabic line must start with an Arabic word"
        blocks = [h for h in hz.lint(os.path.join(cdir, n + ".txt")) if h[0] == "BLOCK"]
        if n.startswith("ai_"):
            assert blocks, f"hzlint finds no BLOCK in {n}"
            for i, para in enumerate(x for x in t.split("\n\n") if x.strip()): assert hz.lint(w(f"{n}{i}.txt", para + "\n")), f"hzlint misses paragraph {i + 1} of {n}"
        else: assert not blocks, f"false positive on {n}: {blocks}"
    ar = lambda n: subprocess.run([sys.executable, os.path.join(root, "modules", "deliverable-visual-qa", "scripts", "arlint.py"), os.path.join(cdir, n)], capture_output=True, text=True)
    assert ar("human_ar.txt").returncode == 0, "arlint flags the human Arabic sample"
    aud = lambda f: subprocess.run([sys.executable, os.path.join(root, "modules", "seo-architect", "scripts", "ai_search_audit.py"), f], capture_output=True, text=True)
    good = '<!doctype html><title>Acme Billing | Invoicing for small teams</title><meta name="description" content="Acme Billing sends invoices, tracks payments and chases late customers so small teams get paid sooner."><link rel="canonical" href="https://acme.example/"><script type="application/ld+json">{"@type":"Organization","name":"Acme Billing"}</script><h1>Get paid sooner</h1>'
    g, b = os.path.join(d, "aud_good"), os.path.join(d, "aud_bad"); os.makedirs(g); os.makedirs(b)
    for dd in (g, b):
        open(os.path.join(dd, "index.html"), "w").write(good); open(os.path.join(dd, "llms.txt"), "w").write("# Acme\n"); open(os.path.join(dd, "robots.txt"), "w").write("User-agent: *\nAllow: /\n"); open(os.path.join(dd, "sitemap.xml"), "w").write("<urlset/>")
    open(os.path.join(b, "broken.html"), "w").write(good.replace('"name":"Acme Billing"}', '"name":'))
    r = aud(g); assert r.returncode == 0 and "0 FAIL" in r.stdout, r.stdout + r.stderr
    r = aud(b); assert r.returncode == 1 and "broken JSON-LD" in r.stdout, r.stdout + r.stderr

def budgets_and_hooks():
    """Context budgets, the telemetry-free guard, and the Stop and SessionStart hooks."""
    root = os.path.join(HERE, "..")
    out = subprocess.run(["sh", os.path.join(root, "hooks", "adams_reminder.sh")], capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    assert len(out) <= 450, f"reminder is {len(out)} chars, max 450"
    R = lambda stdin, tmp: subprocess.run(["sh", os.path.join(root, "hooks", "adams_reminder.sh")], input=stdin, capture_output=True, text=True, env={**os.environ, "TMPDIR": tmp}).stdout
    rt = tempfile.mkdtemp(prefix="adams-rem-")
    try:
        assert R('{"session_id":"s1"}', rt) == out and R('{"session_id":"s1"}', rt) == "", "reminder must print once per session_id"
        assert R('{"session_id":"s2"}', rt) == out, "a new session_id must print again"
        assert R("", rt) == out and R("", rt) == out, "without a session_id the reminder prints every time"
    finally: shutil.rmtree(rt, ignore_errors=True)
    assert len(open(os.path.join(root, "SKILL.md"), encoding="utf-8").read().splitlines()) <= 65, "SKILL.md is over 65 lines"
    for f, cap in (("ALWAYS.md", 950), ("SKILL.md", 1750), ("modules/workflow/GUIDE.md", 1530), ("modules/humanize-writing/GUIDE.md", 3000)):  # est tokens (chars/4), real size plus ~10%
        n = len(open(os.path.join(root, f), encoding="utf-8").read()) // 4
        assert n <= cap, f"{f} is ~{n} est tokens, max {cap}"
    for f in os.listdir(os.path.join(root, "hooks")):
        if f.endswith((".py", ".sh")) and f != "adams_update.sh":
            assert not re.search(r"\b(import|from)\s+(urllib|socket|http|requests)\b", open(os.path.join(root, "hooks", f), encoding="utf-8").read()), f"hooks/{f} imports a network module"
    t = tempfile.mkdtemp(prefix="adams-hook-")
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    H = lambda name, payload: subprocess.run([sys.executable, os.path.join(root, "hooks", name)], input=_json.dumps(payload), capture_output=True, text=True, env=env)
    try:
        subprocess.run(["git", "init", "-q"], cwd=t, env=env)
        open(os.path.join(t, "bad.txt"), "w").write("This is a game-changer.\n")
        r = H("adams_stop.py", {"cwd": t}); assert r.returncode == 0 and _json.loads(r.stdout)["decision"] == "block", r.stdout + r.stderr
        r = H("adams_stop.py", {"cwd": t, "stop_hook_active": True}); assert r.returncode == 0 and r.stdout == "", "stop_hook_active must stay silent"
        open(os.path.join(t, "bad.txt"), "w").write("The model reads each line once.\n\nIt keeps one idea per line.\n")
        r = H("adams_stop.py", {"cwd": t}); assert r.returncode == 0 and r.stdout == "", "a clean file must stay silent: " + r.stdout
        r = H("adams_context.py", {"cwd": t}); assert r.returncode == 0 and r.stdout == "", "no decisions file means no output"
        os.makedirs(os.path.join(t, ".adams")); open(os.path.join(t, ".adams", "decisions.md"), "w").write("\n".join(f"- line {i}" for i in range(100)) + "\n")
        r = H("adams_context.py", {"cwd": t}); assert "settled decisions" in r.stdout and "- line 99" in r.stdout and "- line 19\n" not in r.stdout, r.stdout
    finally:
        shutil.rmtree(t, ignore_errors=True)
        try: os.remove(os.path.join(tempfile.gettempdir(), "adams-stop-" + hashlib.sha1(t.encode()).hexdigest() + ".json"))
        except OSError: pass

def gates():
    """Align gate, verify record plus Stop gate, and commit gate, run as hooks against a temp git repo with its own TMPDIR for the session state."""
    root = os.path.join(HERE, "..")
    t = tempfile.mkdtemp(prefix="adams-gates-")
    repo = os.path.realpath(os.path.join(t, "repo")); os.makedirs(repo)
    env = {k: v for k, v in os.environ.items() if not k.startswith("ADAMS_")}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t", TMPDIR=t, ADAMS_REVIEW="0")  # the review gate is off here; its own cases below turn it on with ADAMS_REVIEW=""
    def H(name, payload, **e):
        raw = payload if isinstance(payload, str) else _json.dumps(payload)
        return subprocess.run([sys.executable, os.path.join(root, "hooks", name)], input=raw, capture_output=True, text=True, env={**env, **e})
    G = lambda *a: subprocess.run(["git", *a], cwd=repo, env=env, capture_output=True, text=True, check=True)
    W = lambda name, text: (os.makedirs(os.path.dirname(os.path.join(repo, name)), exist_ok=True), open(os.path.join(repo, name), "w").write(text))
    edit = lambda sid, f: {"session_id": sid, "cwd": repo, "tool_name": "Edit", "tool_input": {"file_path": os.path.join(repo, f)}}
    commit = lambda sid, msg: {"session_id": sid, "cwd": repo, "tool_name": "Bash", "tool_input": {"command": msg}}
    ran = lambda sid, event, cmd="npm test": {"session_id": sid, "cwd": repo, "hook_event_name": event, "tool_name": "Bash", "tool_input": {"command": cmd}, "tool_response": {"stdout": "", "stderr": "", "interrupted": False}}
    try:
        G("init", "-q"); W("package.json", '{"scripts":{"test":"echo ok"}}'); W("a.py", "print(0)\n"); G("add", "package.json", "a.py"); G("commit", "-qm", "init")
        # align gate
        r = H("adams_align_gate.py", edit("s1", "a.py")); d = _json.loads(r.stdout)["hookSpecificOutput"]
        assert r.returncode == 0 and d["permissionDecision"] == "deny" and "decide --small" in d["permissionDecisionReason"] and d["permissionDecisionReason"].endswith("ADAMS_GATES=0."), r.stdout
        for ok in (edit("s1", "README.md"), edit("s1", ".adams/decisions.md"), edit("s1", ".planning/x.ts"), edit("s9", "../outside.py"), {**edit("s1", "a.py"), "tool_input": {}}):
            assert H("adams_align_gate.py", ok).stdout == "", f"align gate must allow {ok['tool_input']}"
        assert H("adams_align_gate.py", edit("s2", "a.py"), ADAMS_GATES="0").stdout == "", "ADAMS_GATES=0 must open the align gate"
        r = subprocess.run([sys.executable, os.path.join(root, "bin", "adams"), "decide", " "], cwd=repo, capture_output=True, text=True); assert r.returncode == 2, "empty decision must be refused"
        r = subprocess.run([sys.executable, os.path.join(root, "bin", "adams"), "decide", "--small", "x"], cwd=repo, capture_output=True, text=True)
        assert r.returncode == 0 and "small task: x" in open(os.path.join(repo, ".adams", "decisions.md")).read(), r.stdout + r.stderr
        assert H("adams_align_gate.py", edit("s1", "a.py")).stdout == "", "the retry after adams decide must pass"
        assert H("adams_align_gate.py", edit("s1", "a.py")).stdout == "", "and stay open"
        assert H("adams_align_gate.py", "not json").returncode == 0 and H("adams_align_gate.py", "{}").stdout == "", "garbage must never block"
        # verify record and Stop gate (session s1 edited code through the align gate)
        assert H("adams_stop.py", {"session_id": "s1", "cwd": repo}).stdout == "", "no code change yet, nothing to verify"
        W("a.py", "print(1)\n")
        r = H("adams_stop.py", {"session_id": "s1", "cwd": repo}); assert r.returncode == 0 and "last green verification" in _json.loads(r.stdout)["reason"] and "npm test" in r.stdout, r.stdout
        assert H("adams_stop.py", {"session_id": "s1", "cwd": repo, "stop_hook_active": True}).stdout == "", "stop_hook_active must stay silent"
        assert H("adams_stop.py", {"session_id": "s1", "cwd": repo}, ADAMS_VERIFY="0").stdout == "" and H("adams_stop.py", {"session_id": "s1", "cwd": repo}, ADAMS_GATES="0").stdout == "", "opt-outs"
        assert H("adams_stop.py", {"session_id": "s7", "cwd": repo}).stdout == "", "a session that edited no code is never blocked"
        H("adams_verify_record.py", ran("s1", "PostToolUseFailure")); assert "last green" in H("adams_stop.py", {"session_id": "s1", "cwd": repo}).stdout, "a failed run is not green"
        H("adams_verify_record.py", ran("s1", "PostToolUse", "echo hi")); assert "last green" in H("adams_stop.py", {"session_id": "s1", "cwd": repo}).stdout, "a non-verification command is not recorded"
        H("adams_verify_record.py", ran("s1", "PostToolUse")); r = H("adams_stop.py", {"session_id": "s1", "cwd": repo}); assert r.returncode == 0 and r.stdout == "", "a green run on the same tree passes: " + r.stdout
        W("a.py", "print(2)\n"); assert "last green" in H("adams_stop.py", {"session_id": "s1", "cwd": repo}).stdout, "a further edit blocks again"
        H("adams_verify_record.py", "not json")
        # commit gate
        fake = "AKI" + "A" + "IOSFODNN7EXAMPLE"  # built at runtime so this file holds no literal key
        deny = lambda sid, c, **e: H("block-risky-git.py", commit(sid, c), **e)
        W("cfg.js", f'const k = "{fake}";\n'); G("add", "cfg.js")
        r = deny("s3", 'git commit -m "feat: cfg"', ADAMS_VERIFY="0")
        assert r.returncode == 2 and "AWS access key" in r.stderr and "cfg.js:1" in r.stderr and fake not in r.stderr and fake[-4:] in r.stderr and "ADAMS_GATES=0" in r.stderr, r.stderr
        assert deny("s3", 'git commit -m "feat: cfg"', ADAMS_GATES="0").returncode == 0, "ADAMS_GATES=0 must open the commit gate"
        G("reset", "-q"); W("cfg.js", f'const k = "{fake}";\n')
        assert deny("s3", 'git add cfg.js && git commit -m "feat: cfg"', ADAMS_VERIFY="0").returncode == 2, "a secret in a file added by the same command must be caught"
        G("reset", "-q"); os.remove(os.path.join(repo, "cfg.js")); W(".env", "X=1\n"); G("add", "-f", ".env")
        r = deny("s3", 'git commit -m "feat: env"', ADAMS_VERIFY="0"); assert r.returncode == 2 and ".env is an env file" in r.stderr, r.stderr
        G("reset", "-q"); os.remove(os.path.join(repo, ".env")); W(".env.example", "X=\n"); G("add", ".env.example")
        assert deny("s3", 'git commit -m "feat: env example"', ADAMS_VERIFY="0").returncode == 0, ".env.example is allowed"
        G("reset", "-q"); G("add", "a.py")
        r = deny("s3", 'git commit -m "Fix(core): crash"', ADAMS_VERIFY="0"); assert r.returncode == 2 and "regression test" in r.stderr, r.stderr
        W("tests/test_a.py", "assert True\n"); G("add", "tests/test_a.py")
        assert deny("s3", 'git commit -m "fix: crash"', ADAMS_VERIFY="0").returncode == 0, "a fix with a test passes"
        r = deny("s3", 'git commit -m "feat: x"'); assert r.returncode == 2 and "npm test" in r.stderr and "ADAMS_VERIFY=0" in r.stderr, r.stderr
        H("adams_verify_record.py", ran("s3", "PostToolUse")); assert deny("s3", 'git commit -m "feat: x"').returncode == 0, "a green run on the staged tree opens the gate"
        W("a.py", "print(3)\n"); assert deny("s3", 'git commit -m "feat: x"').returncode == 2, "an edit after the green run closes it again"
        G("reset", "-q"); G("checkout", "--", "a.py"); W("NOTES.md", "x\n"); G("add", "NOTES.md")
        assert deny("s4", 'git commit -m "fix: typo"').returncode == 0, "a docs-only fix needs neither a test nor a verification"
        # feature test gate: feat, add and implement need a test-like path next to staged source
        G("reset", "-q"); W("b.py", "print(9)\n"); G("add", "b.py")
        for m in ('feat: b', 'feat(core): b', 'Add b', 'implement b'):
            r = deny("s5", f'git commit -m "{m}"', ADAMS_VERIFY="0"); assert r.returncode == 2 and "new feature needs a test" in r.stderr, f"{m}: {r.stderr}"
        assert deny("s5", 'git commit -m "chore: b"', ADAMS_VERIFY="0").returncode == 0, "only fix and feature messages need a test"
        assert deny("s5", 'git commit -m "Address review notes"', ADAMS_VERIFY="0").returncode == 0, "'Add' must be a whole word"
        W("tests/test_b.py", "assert True\n"); G("add", "tests/test_b.py"); assert deny("s5", 'git commit -m "feat: b"', ADAMS_VERIFY="0").returncode == 0, "a feature with a test passes"
        G("reset", "-q"); G("add", "NOTES.md"); assert deny("s5", 'git commit -m "feat: notes"', ADAMS_VERIFY="0").returncode == 0, "docs-only feature needs no test"
        # review gate: the first commit of a session that stages source is denied once
        G("reset", "-q"); G("add", "b.py")
        r = deny("r1", 'git commit -m "chore: b"', ADAMS_REVIEW="", ADAMS_VERIFY="0")
        assert r.returncode == 2 and "Review before commit" in r.stderr and "correct, safe, holds under load, tested, fast, lean" in r.stderr and "ADAMS_REVIEW=0" in r.stderr, r.stderr
        assert deny("r1", 'git commit -m "chore: b"', ADAMS_REVIEW="", ADAMS_VERIFY="0").returncode == 0, "the retry in the same session passes"
        assert deny("r2", 'git commit -m "chore: b"', ADAMS_REVIEW="", ADAMS_VERIFY="0").returncode == 2, "a new session is reviewed again"
        assert deny("r3", 'git commit -m "chore: b"', ADAMS_REVIEW="", ADAMS_VERIFY="0", ADAMS_GATES="0").returncode == 0, "ADAMS_GATES=0 opens the review gate"
        assert deny("r4", 'git commit -m "chore: b"', ADAMS_REVIEW="0", ADAMS_VERIFY="0").returncode == 0, "ADAMS_REVIEW=0 opens only the review gate"
        G("reset", "-q"); G("add", "NOTES.md"); assert deny("r5", 'git commit -m "docs: notes"', ADAMS_REVIEW="", ADAMS_VERIFY="0").returncode == 0, "no staged source, no review"
        r = deny("r6", 'git commit -m "feat: b"', ADAMS_REVIEW="", ADAMS_VERIFY="0")  # still no source staged
        G("add", "b.py"); r = deny("r6", 'git commit -m "feat: b"', ADAMS_REVIEW="", ADAMS_VERIFY="0")
        assert r.returncode == 2 and "new feature needs a test" in r.stderr and "Review before commit" in r.stderr, "one denial lists every reason: " + r.stderr
        for junk in ("not json", "{}", '{"tool_input":null}', '{"tool_input":{"command":"git commit -m x"},"cwd":"/nonexistent"}'):
            assert H("block-risky-git.py", junk).returncode == 0, f"garbage must never block: {junk}"
    finally:
        shutil.rmtree(t, ignore_errors=True)

def router():
    """The context router: each rule fires on its trigger and only once per session, stays silent otherwise, and never crashes."""
    import importlib.util
    root = os.path.join(HERE, "..")
    t = tempfile.mkdtemp(prefix="adams-router-")
    repo = os.path.realpath(os.path.join(t, "repo")); os.makedirs(repo)
    plain = os.path.realpath(os.path.join(t, "plain")); os.makedirs(plain)  # not a git work tree
    env = {k: v for k, v in os.environ.items() if not k.startswith("ADAMS_")}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t", TMPDIR=t)
    R = lambda payload, **e: subprocess.run([sys.executable, os.path.join(root, "hooks", "adams_router.py")], input=payload if isinstance(payload, str) else _json.dumps(payload), capture_output=True, text=True, env={**env, **e})
    G = lambda *a: subprocess.run(["git", *a], cwd=repo, env=env, capture_output=True, text=True, check=True)
    W = lambda name, text: (os.makedirs(os.path.dirname(os.path.join(repo, name)), exist_ok=True), open(os.path.join(repo, name), "w").write(text))
    prompt = lambda sid, text: {"session_id": sid, "cwd": repo, "hook_event_name": "UserPromptSubmit", "prompt": text}
    def edit(sid, f, tool="Edit", cwd=None, **ti):
        return {"session_id": sid, "cwd": cwd or repo, "hook_event_name": "PostToolUse", "tool_name": tool, "tool_input": {"file_path": os.path.join(cwd or repo, f), **ti}}
    def ctx(r):  # the guidance a PostToolUse payload added ("" for none)
        assert r.returncode == 0, r.stderr
        return _json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"] if r.stdout else ""
    try:
        spec = importlib.util.spec_from_file_location("rt", os.path.join(root, "hooks", "adams_router.py")); rt = importlib.util.module_from_spec(spec); spec.loader.exec_module(rt)
        assert all(len(v) <= 600 for v in rt.TEXT.values()) and set(rt.TEXT) == set(rt.ORDER), "every router block must be 600 characters or less"
        assert all(chr(0x2014) not in v and chr(0x2013) not in v for v in rt.TEXT.values()), "dash in a router block"
        G("init", "-q"); W("package.json", '{"scripts":{"test":"echo ok"},"dependencies":{"a":"1.0.0"}}\n'); W("requirements.txt", "requests>=2\n"); G("add", "package.json", "requirements.txt"); G("commit", "-qm", "init")
        # a. diagnose, from a prompt (English and Arabic) and from a failed test run
        for i, text in enumerate(("the checkout page is broken", "I get an error on save", "الصفحة مش شغال", "في ايرور", "it keeps crashing", "that is a regression")):
            out = R(prompt(f"a{i}", text)).stdout; assert out.startswith("Adams diagnose") and len(out.strip()) <= 600, f"diagnose misses: {text}: {out}"
        assert R(prompt("a0", "still broken")).stdout == "", "a rule fires once per session"
        c = ctx(R({"session_id": "a9", "cwd": repo, "hook_event_name": "PostToolUseFailure", "tool_name": "Bash", "tool_input": {"command": "npm test"}, "error": "x"})); assert c.startswith("Adams diagnose"), c
        assert ctx(R({"session_id": "a8", "cwd": repo, "hook_event_name": "PostToolUseFailure", "tool_name": "Bash", "tool_input": {"command": "ls"}})) == "", "a failed non-test command is not a test failure"
        assert ctx(R({"session_id": "a7", "cwd": repo, "hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": "npm test"}, "tool_response": {"exit_code": 0}})) == "", "a green run adds nothing"
        # b. plain language
        for i, text in enumerate(("مش فاهم", "this is مش واضح", "I don't understand", "please explain simply")):
            assert R(prompt(f"b{i}", text)).stdout.startswith("Adams plain language"), f"plain misses: {text}"
        # c. auth and security, by edited path
        for i, f in enumerate(("src/auth/index.js", "lib/session.ts", "app/login/page.jsx", "db/policies.sql", "src/middleware.ts", "proxy.ts", ".env.local", "api/oauth.go")):
            assert ctx(R(edit(f"c{i}", f))).startswith("Adams security checklist"), f"auth misses: {f}"
        assert "security checklist" not in ctx(R(edit("c9", "src/util/format.ts"))), "an ordinary path is not auth"
        assert "security checklist" not in ctx(R(edit("c10", "docs/session.md"))), "prose is not auth code"
        # d. new dependency: Edit, MultiEdit and Write (compared with git HEAD), other files, a version bump
        pj = lambda sid, new, old='"a": "1.0.0"', tool="Edit": edit(sid, "package.json", tool, old_string=old, new_string=new)
        assert "new dependency" in ctx(R(pj("d1", '"a": "1.0.0",\n"left-pad": "^1.3.0"'))), "Edit adding a package.json dependency"
        assert ctx(R(pj("d2", '"a": "2.0.0"'))) == "", "a version bump adds no dependency"
        assert ctx(R(pj("d2", '"name": "x"', old='"name": "y"'))) == "", "a name change adds no dependency"
        assert "new dependency" in ctx(R(edit("d3", "package.json", "MultiEdit", edits=[{"old_string": "x", "new_string": "y"}, {"old_string": "", "new_string": '"zod": "^3.0.0"'}]))), "MultiEdit"
        assert "new dependency" in ctx(R(edit("d4", "package.json", "Write", content='{"dependencies":{\n"a": "1.0.0",\n"zod": "^3.0.0"\n}}\n'))), "Write with a new name vs git HEAD"
        assert "new dependency" not in ctx(R(edit("d5", "package.json", "Write", content='{"scripts":{"test":"echo ok"},"dependencies":{"a":"1.0.0"}}\n'))), "Write with the same dependencies"
        assert "new dependency" in ctx(R(edit("d6", "requirements.txt", "Write", content="requests>=2\nflask==3.0\n"))), "requirements.txt"
        assert "new dependency" in ctx(R(edit("d7", "pyproject.toml", old_string="", new_string='dependencies = ["rich>=13"]'))), "pyproject.toml"
        assert "new dependency" in ctx(R(edit("d8", "go.mod", old_string="", new_string="require github.com/google/uuid v1.6.0"))), "go.mod"
        assert "new dependency" in ctx(R(edit("d9", "Cargo.toml", old_string="", new_string='serde = "1.0"'))), "Cargo.toml"
        assert ctx(R(edit("d10", "src/x.json", old_string="", new_string='"zod": "^3.0.0"'))) == "" , "only manifests count"
        # e. UI change
        for i, f in enumerate(("a.tsx", "a.jsx", "a.vue", "a.svelte", "a.css", "a.scss", "a.html")):
            assert "Adams UI check" in ctx(R(edit(f"e{i}", f))) and "375, 768 and 1440" in ctx(R(edit(f"e{i}x", f))), f"ui misses: {f}"
        assert "Adams UI check" not in ctx(R(edit("e9", "a.py"))), "a python file is not UI"
        # f. tests first: the first source edit when no test was edited yet and the project has tests
        assert "Adams tests first" in ctx(R(edit("f1", "src/lib.py"))), "first source edit"
        assert ctx(R(edit("f1", "src/other.py"))) == "", "and only once"
        assert ctx(R(edit("f2", "tests/test_lib.py"))) == "" and ctx(R(edit("f2", "src/lib.py"))) == "", "a test edited first means tests are first"
        assert ctx(R(edit("f3", "latest.py"))).startswith("Adams tests first"), "'latest' is not a test file"
        assert ctx(R(edit("f4", "README.md", old_string="a", new_string="b"))).startswith("Adams published copy"), "docs are not source"
        assert ctx(R(edit("f5", "src/lib.py", cwd=plain))) == "", "outside a git work tree there is nothing to detect"
        assert ctx(R(edit("f6", "../outside.py"))) == "", "a path outside the project is ignored"
        # g. prose deliverable
        for i, f in enumerate(("README.md", "docs/guide.md", "posts/launch.txt", "content/about.md", "README.fr.md")):
            assert ctx(R(edit(f"g{i}", f))).startswith("Adams published copy") and "minimum effective edit" in ctx(R(edit(f"g{i}x", f))), f"prose misses: {f}"
        for i, f in enumerate((".adams/decisions.md", ".planning/notes.md", "notes.md", "src/a.md")):
            assert ctx(R(edit(f"g9{i}", f))) == "", f"not published copy: {f}"
        # priority and cap: three rules match one edit, two print now and the third on the next call
        c = ctx(R(edit("m1", "src/auth/Login.tsx"))); assert "security checklist" in c and "tests first" in c and "UI check" not in c, c
        assert ctx(R(edit("m1", "src/auth/Other.tsx"))).startswith("Adams UI check"), "the held back rule fires on the next call"
        # silence, opt-out and garbage
        assert R(prompt("n1", "add a nice footer")).stdout == "", "no rule matches"
        assert R(prompt("n2", "the build is broken"), ADAMS_GATES="0").stdout == "" and ctx(R(edit("n2", "src/auth/Login.tsx"), ADAMS_GATES="0")) == "", "ADAMS_GATES=0 silences the router"
        assert R({"session_id": "n3", "cwd": repo, "prompt": 5}).stdout == ""
        for junk in ("not json", "{}", "[]", "null", '{"prompt":null}', '{"tool_name":"Edit","tool_input":null}', '{"tool_name":"Edit","tool_input":{"file_path":5}}', '{"tool_name":"Bash","tool_input":{"command":null},"cwd":"/nonexistent"}', '{"tool_name":"Edit","tool_input":{"file_path":"x"},"cwd":"/nonexistent"}'):
            r = R(junk); assert r.returncode == 0 and r.stdout == "" and "Traceback" not in r.stderr, f"garbage must never crash or print: {junk}: {r.stdout}{r.stderr}"
        hj = _json.load(open(os.path.join(root, "hooks", "hooks.json")))["hooks"]
        for event in ("UserPromptSubmit", "PostToolUse", "PostToolUseFailure"):
            hs = [h for gr in hj[event] for h in gr["hooks"] if "adams_router.py" in h["command"]]
            assert len(hs) == 1 and hs[0]["timeout"] <= 5, f"hooks.json must register the router once on {event} with a small timeout"
        assert [gr["matcher"] for gr in hj["PostToolUse"] if "adams_router.py" in gr["hooks"][0]["command"]] == ["Edit|Write|MultiEdit|Bash"]
        src = open(os.path.join(root, "bin", "adams"), encoding="utf-8").read()
        assert src.count("adams_router.py") == 3, "bin/adams HOOKS must register the router on UserPromptSubmit, PostToolUse and PostToolUseFailure"
    finally: shutil.rmtree(t, ignore_errors=True)

def web_routes():
    """A hash-routed page is many pages: the crawl must scan every view, plain #anchors stay one page, and coverage shows in the verdict."""
    import socket
    page = lambda nav: ('<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><body style="margin:0;font:16px/1.4 Arial"><nav>' + nav +
        '</nav><main id=m></main><script>var V={a:"<h2>Alpha</h2><p>Short clean view.</p>",b:"<h2>Beta</h2><p style=\\"width:220px\\">Short words fill every line here until Supercalifragilisticexpialidocious</p>"};'
        'function r(){m.innerHTML=V[location.hash.slice(2)]||V.a}addEventListener("hashchange",r);r()</script>')
    w("spa.html", page('<a href="#/a">A</a> <a href="#/b">B</a>')); w("anchors.html", page('<a href="#top">A</a> <a href="#more">B</a>'))
    w("one.txt", "/spa.html#/a\n")
    head = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><body style="margin:0;font:16px/1.4 Arial">'
    w("role.html", head + '<div class=stagecard style="width:200px"><p>Seven plain words that wrap onto two lines</p></div><span class=zz style="display:inline-block;width:110px">Four short chip words</span>')
    w("shrink.html", head + '<p id=p style="width:300px">Shrunk by a script</p><script>addEventListener("load",()=>{p.style.fontSize="12.5px"})</script>')
    w("noshrink.html", head + '<p style="width:300px;font-size:12.5px">Static size in the markup</p>')
    with socket.socket() as so: so.bind(("", 0)); port = so.getsockname()[1]
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    WB = lambda *a: subprocess.run(["node", os.path.join(HERE, "..", "modules", "line-balance", "scripts", "web_balance.js"), "--widths", "375", *a], capture_output=True, text=True, env={**os.environ, "ADAMS_AUTO_INSTALL": "0"})
    try:
        time.sleep(1); u = f"http://127.0.0.1:{port}/"
        r = WB("--base", u + "spa.html#/a", "--crawl")
        if r.returncode == 2: print("note: Playwright or Chromium missing, web route cases skipped"); return
        assert r.returncode == 1 and "#/b" in r.stdout and "PAGES 2" in r.stdout and "ROUTES 2" in r.stdout and "FLAGGED 1\n" in r.stdout, "crawl must scan both hash routes: " + r.stdout + r.stderr
        r = WB("--base", u + "anchors.html", "--crawl"); assert r.returncode == 0 and "PAGES 1" in r.stdout and "WARNING" not in r.stdout, "plain #anchors are one page: " + r.stdout
        r = WB("--base", u, "--urls", os.path.join(d, "one.txt")); assert "WARNING 1 in-page routes were not scanned" in r.stdout and "PAGES 1" in r.stdout, "unscanned routes must warn: " + r.stdout
        rc, out = check(os.path.join(d, "spa.html")); assert rc == 1 and re.search(r"ADAMS CHECK: FLAGGED \(\d+ pages x 3 widths\)", out), "verdict must state coverage: " + out
        rc, out = check(os.path.join(d, "spa.html"), "--", "--urls", os.path.join(d, "one.txt")); assert "(use --crawl or --urls)\nADAMS CHECK:" in out and "CLEAN (1 page x 3 widths, WARNING 1 in-page routes were not scanned)" in out, "warning must reach the verdict: " + out
        r = WB("--base", u + "role.html"); assert "WRAPPED" in r.stdout and "zz" in r.stdout and not re.search(r"WRAPPED.*stagecard", r.stdout), "short text is told by rendering, not class name: " + r.stdout
        r = WB("--base", u + "shrink.html"); assert "SHRUNK" in r.stdout and r.returncode == 1, "runtime font-size changes must be flagged: " + r.stdout
        r = WB("--base", u + "noshrink.html"); assert "SHRUNK" not in r.stdout, "static font-size must not be flagged: " + r.stdout
    finally: srv.terminate()

try:
    versioning()
    budgets_and_hooks()
    gates()
    router()
    authorship()
    standalone()
    corpus_and_audit()
    reminder_text()
    plugin_guard()
    update_flow()
    project_tools()
    profile_split()
    git_guard()
    packaging()
    router_integrity()
    hz_coverage()
    lang_coverage()
    web_routes()
    rc, out = check(w("bad.txt", "This is a game-changer.\n"));              assert rc == 1 and "STOCK PHRASE" in out, out
    rc, out = check(w("README.md", "# Title\n\nThe model reads each line once.\n\n- **Label:** one\n- **Label:** two\n")); assert "hzlint --doc" in out and "--reply" not in out, "README must be checked as a document, not as a reply: " + out
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
    refs = {"modules/workflow": ("diagnose.md", "handoff.md", "retro.md"),
            "modules/humanize-writing": ("linkedin-post.md", "english-tells.md"),
            "modules/product-principles": ("conversion-psychology.md", "funnel-map.md", "dark-patterns.md"),
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
