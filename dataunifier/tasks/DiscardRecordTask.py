"""
DiscardRecordTask module.
"""

from dataunifier.common.exceptions import DiscardRecordException
from dataunifier.tasks.AbstractTask import AbstractRegularTask


K_DISCARD_RECORD = "discard_record"


class DiscardRecordTask(AbstractRegularTask):
    """
    Discards an entire record.
    """

    @classmethod
    def create_from_config(cls, task_parsing_context):
        name = task_parsing_context.task_name
        when = task_parsing_context.when
        previous_task = task_parsing_context.previous_task
        resulting_fields = previous_task.get_resulting_fields() if previous_task else None
        return DiscardRecordTask(name, when, resulting_fields)

    @classmethod
    def get_task_type_string(cls):
        return K_DISCARD_RECORD

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, resulting_fields):
        super(DiscardRecordTask, self).__init__(name, when)
        self.resulting_fields = resulting_fields

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.name == other.name,
            self.when == other.when,
            self.resulting_fields == other.resulting_fields
        ])

    def __str__(self):
        return "DiscardRecordTask(%s, %s, %s)" % (
            self.name, self.when, self.resulting_fields
        )

    def __repr__(self):
        return str(self)

    def transform(self, row_ctxt):
        if (self.when and self.when.evaluate(row_ctxt)) or self.when is None:
            raise DiscardRecordException()
        return row_ctxt

    def get_resulting_fields(self):
        return self.resulting_fields
