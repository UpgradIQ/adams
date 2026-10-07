# Contributing

Thank you for helping. Small, focused pull requests are easiest to review.

1. Fork, create a branch, change one thing.
2. Run `python3 scripts/selftest.py`. It must print `selftest OK`; CI runs it on a fresh clone.
3. A new lint rule needs a sample the rule must flag and, where it can misfire, a clean sample it must not flag, both in `scripts/selftest.py`.
4. Rules and word lists live in `scripts/` and `modules/*/scripts/`. Guides point to them and never paste code.
5. Nothing in the repository may depend on one person's machine, paths, language or taste. Personal preferences belong in a profile (`~/.config/adams/profiles/`), not in the shipped modules.
6. No em or en dashes in shipped text. Keep guides short and concrete.

By contributing you agree that your contribution is licensed under the MIT License.
