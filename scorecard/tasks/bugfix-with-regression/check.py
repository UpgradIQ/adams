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

def hidden():
    return c.run_hidden(repo, os.path.join(HERE, "hidden"), UNITTEST)

def regression_catches_bug():
    """The tests in the repo must fail against the original, buggy slug.py: a test that passes on both guards nothing."""
    import shutil, subprocess, tempfile
    t = tempfile.mkdtemp(prefix="scorecard-reg-")
    try:
        dst = os.path.join(t, "repo"); shutil.copytree(repo, dst, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        shutil.copy(os.path.join(HERE, "fixture", "slug.py"), os.path.join(dst, "slug.py"))
        r = subprocess.run(UNITTEST, cwd=dst, capture_output=True, text=True, timeout=60, env={**os.environ, "PYTHONPATH": dst, "PYTHONDONTWRITEBYTECODE": "1"})
        return r.returncode != 0, "the repo's tests still pass on the original bug"
    finally: shutil.rmtree(t, ignore_errors=True)

sys.exit(c.main([
    (0.6, "hidden slugify tests pass", hidden),
    (0.1, "a test case was added", lambda: test_defs(repo) > test_defs(os.path.join(HERE, "fixture"))),
    (0.3, "the added tests fail on the original code (a real regression test)", regression_catches_bug),
]))
