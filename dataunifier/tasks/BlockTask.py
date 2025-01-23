"""
BlockTask module.
"""

from dataunifier.tasks.AbstractTask import AbstractTask

K_BLOCK = "block"


class BlockTask(AbstractTask):
    """
    A task that contains other tasks.

    Mainly for use in situations where you need to apply the same "when" condition to multiple tasks.
    """

    @classmethod
    def get_task_type_string(cls):
        return K_BLOCK

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, task_list):
        super(BlockTask, self).__init__(name, when)
        self.task_list = task_list

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.name == other.name,
            self.when == other.when,
            self.task_list == other.task_list
        ])

    def __str__(self):
        return f"BlockTask({self.name}, {self.when}, {self.task_list})"

    def __repr__(self):
        return str(self)

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        output = row_ctxt
        for task in self.task_list:
            output = task.transform(output)
        return output

    def get_resulting_fields(self):
        return self.task_list[-1].get_resulting_fields()
