"""
Module containing logic to produce the correct Task object from the configuration.
"""

from dataunifier.common.exceptions import NoSuchTaskException
from dataunifier.tasks import ALL_TASK_CLASSES


def get_task(ctxt):
    """
    Get the right Task object corresponding to the configuration block.

    :param TaskParsingContext ctxt: The context object for the configuration block corresponding to the task.
    :return: The task object.
    :rtype: AbstractTask
    """

    for task_class in ALL_TASK_CLASSES:
        if ctxt.task_type == task_class.get_task_type_string():
            return task_class.create_from_config(ctxt)
    raise NoSuchTaskException(ctxt.task_type)
