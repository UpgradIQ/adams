import unittest

from textutils import truncate_words


class HiddenTruncateTest(unittest.TestCase):
    def test_drops_extra_words(self):
        self.assertEqual(truncate_words("one two three four", 2), "one two...")

    def test_exact_limit_is_unchanged(self):
        self.assertEqual(truncate_words("one two", 2), "one two")

    def test_joins_with_single_spaces_when_cut(self):
        self.assertEqual(truncate_words("one  two   three", 2), "one two...")

    def test_unchanged_keeps_original_spacing(self):
        self.assertEqual(truncate_words("  keep  spacing  ", 5), "  keep  spacing  ")

    def test_empty(self):
        self.assertEqual(truncate_words("", 3), "")

    def test_bad_limit(self):
        with self.assertRaises(ValueError):
            truncate_words("a b", 0)
        with self.assertRaises(ValueError):
            truncate_words("a b", -1)
