"""
Module containing the abstract base classes for all :code:`when` objects.
"""

import abc


class AbstractWhen(abc.ABC):
    """
    Abstract base class for a :code:`when` object.
    """

    @abc.abstractmethod
    def evaluate(self, row_ctxt):
        """
        Evaluate whether a row fulfils the :code:`when` criteria.

        :param ParseRowContext row_ctxt: The context containing the row.
        :return: True if the row fulfils the criteria, False otherwise.
        :rtype: bool
        """


class AbstractRegularWhen(AbstractWhen):
    """
    Abstract base class for regular :code:`when` objects that are to be created from a YAML block.
    """

    @classmethod
    @abc.abstractmethod
    def create_from_config(cls, when_parsing_context):
        """
        Create the :code:`when` object from the :code:`when` block in the configuration file.

        :param WhenParsingContext when_parsing_context: The context for the configuration block.
        :return: The "when" object.
        :rtype: AbstractRegularWhen
        """

    @classmethod
    @abc.abstractmethod
    def get_key_set(cls):
        """
        Get the set of YAML keys that uniquely identifies this particular type of :code:`when` object.

        :return: The set of YAML keys.
        :rtype: set[str]
        """
