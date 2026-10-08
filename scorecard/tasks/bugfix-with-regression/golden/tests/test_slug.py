import unittest

from slug import slugify


class SlugTest(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_punctuation_and_edges(self):
        self.assertEqual(slugify("  Hello,  World!! "), "hello-world")


if __name__ == "__main__":
    unittest.main()
