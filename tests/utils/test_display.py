import unittest

from dataunifier.utils.display import ProgressBar


class TestProgressBar(unittest.TestCase):
    def test_zero_total(self):
        obj1 = ProgressBar(0)
        obj1.close()
