#!/usr/bin/env python3
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import common as c
HERE = os.path.dirname(os.path.abspath(__file__))
repo, _, ev = c.args()

def test_defs(root):
    n = 0
    for d, _, fs in os.walk(os.path.join(root, "tests")):
        for f in fs:
            if f.endswith(".py"): n += len(re.findall(r"^\s*def test_", open(os.path.join(d, f), encoding="utf-8").read(), re.M))
    return n

UNITTEST = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]

def tests_mention():
    hit = 0
    for d, _, fs in os.walk(os.path.join(repo, "tests")):
        for f in fs:
            if f.endswith(".py") and "truncate_words" in open(os.path.join(d, f), encoding="utf-8").read(): hit += 1
    return hit > 0 and test_defs(repo) > test_defs(os.path.join(HERE, "fixture"))

def tests_first():
    paths = [p for _, _, p in c.edits(ev)]  # edit tools and shell writes (cat >>, tee, sed -i, python open(...,"w")), absolute or relative paths
    is_test = lambda p: bool(re.search(r"(^|/)(tests?/|test_[^/]*$|[^/]*_test\.py$)", p))
    first_test = next((i for i, p in enumerate(paths) if is_test(p)), None)
    first_src = next((i for i, p in enumerate(paths) if p.endswith("textutils.py") and not is_test(p)), None)
    if first_src is None: return False, "no edit to textutils.py in the transcript"
    return first_test is not None and first_test < first_src, "textutils.py was edited before any test file"

sys.exit(c.main([
    (0.4, "hidden truncate_words tests pass", lambda: c.run_hidden(repo, os.path.join(HERE, "hidden"), UNITTEST)),
    (0.3, "a test for truncate_words exists in the repo", tests_mention),
    (0.3, "a test file was edited before textutils.py", tests_first, True),
]))
