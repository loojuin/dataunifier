"""
Module for the :code:`Or` class.
"""

from dataunifier.when.Abstract import AbstractWhen


class Or(AbstractWhen):
    """
    Represents an "or" condition on multiple :code:`when` conditions.
    """

    def __init__(self, when_list):
        """
        Create an :code:`Or` object.

        :param list[AbstractWhen] when_list: The list of conditions to be "or"ed.
        """

        super(Or, self).__init__()
        self.when_list = when_list

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.when_list == other.when_list
        ])

    def evaluate(self, row_ctxt):
        for when in self.when_list:
            if when.evaluate(row_ctxt):
                return True
        return False
