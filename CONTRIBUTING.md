# Contributing

Thank you for helping. Small, focused pull requests are easiest to review.

1. Fork, create a branch, change one thing.
2. Run `python3 scripts/selftest.py`. It must print `selftest OK`; CI runs it on a fresh clone.
3. A new lint rule needs a sample the rule must flag and, where it can misfire, a clean sample it must not flag, both in `scripts/selftest.py`.
4. Rules and word lists live in `scripts/` and `modules/*/scripts/`. Guides point to them and never paste code.
5. Nothing in the repository may depend on one person's machine, paths, language or taste. Personal preferences belong in a profile (`~/.config/adams/profiles/`), not in the shipped modules.
6. No em or en dashes in shipped text. Keep guides short and concrete.

## How the repository is protected

`main` takes changes through pull requests that pass the `selftest` check, and force pushes and deletions are blocked. Release tags (`v*`) cannot be moved or deleted, because every update follows them. The maintainer can bypass these rules for emergencies.

## Releasing (maintainers)

Put the notes under `## Unreleased` in `CHANGELOG.md` as you merge. To release: `python3 scripts/release.py X.Y.Z` (it moves the notes under the version, bumps `VERSION` and the plugin manifest, runs the selftest, commits and tags), then `git push origin main --follow-tags`. The release workflow publishes the GitHub Release, and users on a clone update to the new tag on their next session.

By contributing you agree that your contribution is licensed under the MIT License.
