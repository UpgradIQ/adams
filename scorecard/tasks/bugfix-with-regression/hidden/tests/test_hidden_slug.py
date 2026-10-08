import unittest

from slug import slugify


class HiddenSlugTest(unittest.TestCase):
    def test_punctuation_and_edges(self):
        self.assertEqual(slugify("  Hello,  World!! "), "hello-world")

    def test_ampersand(self):
        self.assertEqual(slugify("Rock & Roll"), "rock-roll")

    def test_only_separators_around(self):
        self.assertEqual(slugify("---a---"), "a")

    def test_runs_collapse(self):
        self.assertEqual(slugify("a  b   c"), "a-b-c")

    def test_empty_and_symbols(self):
        self.assertEqual(slugify(""), "")
        self.assertEqual(slugify("***"), "")

    def test_already_a_slug(self):
        self.assertEqual(slugify("already-slugged"), "already-slugged")
