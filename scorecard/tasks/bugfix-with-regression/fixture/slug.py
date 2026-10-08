import re


def slugify(text):
    """Lowercase the text and join its words with hyphens."""
    return re.sub(r"[^a-z0-9]", "-", text.lower())
