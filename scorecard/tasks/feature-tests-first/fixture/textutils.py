def title_case(text):
    """Capitalise every word and join them with single spaces."""
    return " ".join(word.capitalize() for word in text.split())


def reverse_words(text):
    """Reverse the order of the words, joined by single spaces."""
    return " ".join(reversed(text.split()))
