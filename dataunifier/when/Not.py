"""
Module for the :code:`Not` class.
"""

from dataunifier.when.Abstract import AbstractWhen


class Not(AbstractWhen):
    """
    Negates a :code:`when` condition.
    """

    def __init__(self, when):
        """
        Create a :code:`Not` object.

        :param AbstractWhen when: The condition to negate.
        """

        super(Not, self).__init__()
        self.when = when

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.when == other.when
        ])

    def evaluate(self, row_ctxt):
        return not self.when.evaluate(row_ctxt)
