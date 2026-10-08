`slugify("  Hello,  World!! ")` in slug.py returns `--hello---world---`. It should return `hello-world`: lowercase words joined by single hyphens, with no hyphen at the start or the end. Fix it.
