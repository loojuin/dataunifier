import unittest

from dataunifier.common import constants
from dataunifier.common.exceptions import SyntaxException


class TestSyntaxException(unittest.TestCase):
    def test_get_message_for_print(self):
        input1 = "This is a test."
        correct1 = "%s: %s" % (constants.SYNTAX_EXCEPTION_PREFIX, input1)
        output1 = SyntaxException(input1).get_message_for_print()
        self.assertEqual(correct1, output1)
