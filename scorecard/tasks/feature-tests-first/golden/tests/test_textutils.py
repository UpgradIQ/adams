import unittest

from textutils import reverse_words, title_case, truncate_words


class TextUtilsTest(unittest.TestCase):
    def test_title_case(self):
        self.assertEqual(title_case("hello big  world"), "Hello Big World")

    def test_reverse_words(self):
        self.assertEqual(reverse_words("one two three"), "three two one")

    def test_truncate_words(self):
        self.assertEqual(truncate_words("one two three", 2), "one two...")
        self.assertEqual(truncate_words("one two", 2), "one two")
        with self.assertRaises(ValueError):
            truncate_words("one", 0)


if __name__ == "__main__":
    unittest.main()
