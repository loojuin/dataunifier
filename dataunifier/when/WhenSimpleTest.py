"""
Module for the :code:`WhenSimpleTest` class.
"""

from dataunifier.when.Abstract import AbstractRegularWhen


class WhenSimpleTest(AbstractRegularWhen):
    """
    A simple test class that allows the tester to determine whether the "when" condition returns :code:`True`
    or :code:`False`.
    """

    @classmethod
    def create_from_config(cls, when_parsing_context):
        raise Exception("This method should never be called.")

    @classmethod
    def get_key_set(cls):
        raise Exception("This method should never be called.")

    def __init__(self, some_string=""):
        """
        Create a :code:`WhenSimpleTest` object.

        :param str some_string: An arbitrary string that determines the result of the "evaluate" method. If the string
                                is empty, the "evaluate" method will return "False". Otherwise, it will return "True".
        """

        self.some_string = some_string
        super(WhenSimpleTest, self).__init__()

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return self.some_string == other.some_string

    def evaluate(self, row_ctxt):
        if self.some_string:
            return True
        return False
