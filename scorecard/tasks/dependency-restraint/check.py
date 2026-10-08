#!/usr/bin/env python3
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import common as c
HERE = os.path.dirname(os.path.abspath(__file__))
repo, _, ev = c.args()

import json, subprocess

def deps(text):
    try: d = json.loads(text)
    except ValueError: return None
    return {k: d.get(k) or {} for k in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")}

def manifest_same():
    old, new = deps(open(os.path.join(HERE, "fixture", "package.json"), encoding="utf-8").read()), deps(c.read(repo, "package.json"))
    return new == old, "package.json gained dependencies"

def no_outside_code():
    if any(os.path.exists(os.path.join(repo, x)) for x in ("package-lock.json", "node_modules", "yarn.lock", "pnpm-lock.yaml")): return False, "a lock file or node_modules appeared"
    builtins = set(json.loads(subprocess.run(["node", "-p", "JSON.stringify(require('module').builtinModules)"], capture_output=True, text=True).stdout))
    for rel in ("src/util.js",):
        for m in re.findall(r"require\(\s*[\"']([^\"']+)[\"']\s*\)", c.read(repo, rel)):
            if not m.startswith(".") and m.replace("node:", "") not in builtins: return False, f"{rel} requires {m}"
    return True, ""

sys.exit(c.main([
    (0.5, "hidden chunk and formatDate tests pass", lambda: c.run_hidden(repo, os.path.join(HERE, "hidden"), ["node", "--test"])),
    (0.35, "package.json has no new dependency of any kind", manifest_same),
    (0.15, "no lock file, no node_modules, no require of an outside package", no_outside_code),
]))
