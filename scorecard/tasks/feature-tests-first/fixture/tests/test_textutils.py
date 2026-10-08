import unittest

from textutils import reverse_words, title_case


class TextUtilsTest(unittest.TestCase):
    def test_title_case(self):
        self.assertEqual(title_case("hello big  world"), "Hello Big World")

    def test_reverse_words(self):
        self.assertEqual(reverse_words("one two three"), "three two one")


if __name__ == "__main__":
    unittest.main()
