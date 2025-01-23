"""
Module containing abstract base classes for all tasks.
"""

import abc


class AbstractTask(abc.ABC):
    """
    Abstract base class for all task types.
    """

    @classmethod
    @abc.abstractmethod
    def get_task_type_string(cls):
        """
        Get the task type label as a string.

        :return: The task type label.
        :rtype: str
        """

    @classmethod
    @abc.abstractmethod
    def is_conditional(cls):
        """
        Indicates whether the task can be used with conditionals (i.e., "when").

        :return: True if the task can be used with conditions, False otherwise.
        :rtype: bool
        """

    def __init__(self, name, when):
        """
        Super constructor for all task types.

        :param str name: The name of the task.
        :param AbstractWhen when: The When object for the task.
        """

        self.name = name
        self.when = when

    @abc.abstractmethod
    def transform(self, row_ctxt):
        """
        Transform a row of data.

        :param ParseRowContext row_ctxt: The row context object to transform.
        :return: The transformed row context object.
        :rtype: ParseRowContext
        """

    @abc.abstractmethod
    def get_resulting_fields(self):
        """
        Get the list of fields that result after the row is transformed.

        :return: The list of fields.
        :rtype: list[str]
        """

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.name == other.name,
            self.when == other.when
        ])


class AbstractRegularTask(AbstractTask):
    """
    Abstract parent class for all tasks that can be created from the config context.
    """

    @classmethod
    @abc.abstractmethod
    def create_from_config(cls, task_parsing_context):
        """
        Create the task object from the configuration.

        :param TaskParsingContext task_parsing_context: The context object for the configuration block for the task.
        :return: The task object.
        :rtype: AbstractRegularTask
        """
