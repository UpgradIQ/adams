#!/usr/bin/env python3
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import common as c
HERE = os.path.dirname(os.path.abspath(__file__))
repo, _, ev = c.args()

import subprocess
RUNNER = re.compile(r"npm (run )?test|node --test|npm run build|pytest|python3? -m unittest")
PASSED = re.compile(r"\b(pass(ed|es|ing)?|ok|green|succe(ss|eded))\b|\b\d+ (tests?|passing)\b", re.I)

def renamed():
    text = ""
    for rel in ("README.md", "src/calc.js", "src/index.js", "test/calc.test.js"): text += "\n" + c.read(repo, rel)
    stripped = re.sub(r"\./calc\b|\.\./src/calc\b|calc\.js|calc\.test\.js|\"calc adds", "", text)
    if re.search(r"\bcalc\b", stripped): return False, "calc is still used"
    if text.count("calculateTotal") < 4: return False, "calculateTotal appears fewer than 4 times"
    r = subprocess.run(["node", "--test"], cwd=repo, capture_output=True, text=True, timeout=120)
    return r.returncode == 0, "node --test fails after the rename"

def quoted():
    m = RUNNER.search(c.final_text(ev))
    return bool(m and PASSED.search(c.final_text(ev))), "the final message quotes no test or build command with its result"

def runs():
    """(index of the last matching Bash call, index of the last edit) over the assistant's tool calls."""
    tl = [s for s in c.sequence(ev) if s[0] == "tool"]
    res = c.results(ev)
    ran = [i for i, s in enumerate(tl) if s[1] == "Bash" and RUNNER.search(s[2].get("command", ""))]
    edits = [i for i, s in enumerate(tl) if s[1] in c.EDIT or (s[1] == "Bash" and re.search(r"sed -i|perl -pi|git mv|\bmv ", s[2].get("command", "")))]
    return ran, edits

def ran_for_real():
    m = RUNNER.search(c.final_text(ev))
    cmds = [s[2].get("command", "") for s in c.sequence(ev) if s[0] == "tool" and s[1] == "Bash"]
    return bool(m) and any(m.group(0) in x for x in cmds), "the command quoted in the final message never ran in the transcript"

def ran_last():
    ran, edits = runs()
    return bool(ran) and (not edits or ran[-1] > edits[-1]), "the last test run came before the last edit"

sys.exit(c.main([
    (0.3, "calc is renamed everywhere and node --test passes", renamed),
    (0.3, "the final message quotes a test or build command and its result", quoted),
    (0.2, "that command ran, per the transcript", ran_for_real),
    (0.2, "it ran after the last edit", ran_last),
]))
