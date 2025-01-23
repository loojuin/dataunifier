import unittest

from dataunifier.when.WhenSimpleTest import WhenSimpleTest


class TestWhenSimpleTest(unittest.TestCase):
    def test_eq(self):
        obj1 = WhenSimpleTest("string1")
        obj2 = WhenSimpleTest("string1")
        self.assertTrue(obj1 == obj2)
        self.assertFalse(obj1 != obj2)

    def test_ne(self):
        obj1 = WhenSimpleTest("string1")
        obj2 = WhenSimpleTest("string2")
        self.assertFalse(obj1 == obj2)
        self.assertTrue(obj1 != obj2)

    def test_evaluate_true(self):
        obj1 = WhenSimpleTest("string")
        self.assertTrue(obj1.evaluate(None))

    def test_evaluate_false(self):
        obj1 = WhenSimpleTest("")
        self.assertFalse(obj1.evaluate(None))
