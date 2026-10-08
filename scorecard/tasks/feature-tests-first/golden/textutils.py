def title_case(text):
    """Capitalise every word and join them with single spaces."""
    return " ".join(word.capitalize() for word in text.split())


def reverse_words(text):
    """Reverse the order of the words, joined by single spaces."""
    return " ".join(reversed(text.split()))


def truncate_words(text, limit):
    """First `limit` words joined by single spaces plus "..." when words were dropped; short text is returned unchanged."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]) + "..."
