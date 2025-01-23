import unittest

from dataunifier.utils import regex


class TestRegexify(unittest.TestCase):
    def test(self):
        input1 = "The quick (brown) {fox} jumps* over the lazy dog - *sometimes+."
        correct1 = "^The\\ quick\\ \\(brown\\)\\ \\{fox\\}\\ jumps\\*\\ over\\ the\\ lazy\\ dog\\ \\-\\ " \
                   "\\*sometimes\\+\\.$"
        output1 = regex.regexify(input1)
        self.assertEqual(correct1, output1)
