"""
DiscardFieldsTask module.
"""

from dataunifier.common.exceptions import ConfigException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper, display

K_DISCARD_FIELDS = "discard_fields"
K_FIELDS = "fields"


def _validate_field_mapping(task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_task_fields = set(previous_task.get_resulting_fields())
    for field in task.field_list:
        if field not in previous_task_fields:
            msg = 'Field "%s" is supposed to be dropped by task "%s", but was not found in the' \
                  'resulting fields of preceding %s task "%s". (File "%s")' % (
                      field, task.name, previous_task.get_task_type_string(), previous_task.name, current_file
                  )
            display.warn(msg)


class DiscardFieldsTask(AbstractRegularTask):
    """
    Task that discards fields from the row.
    """

    @classmethod
    def create_from_config(cls, task_parsing_context):
        valid_keys = {K_FIELDS}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        name = task_parsing_context.task_name
        if task_parsing_context.when is not None:
            msg = '"when" cannot be used with a %s task. (File "%s", task "%s")' % (
                K_DISCARD_FIELDS, task_parsing_context.current_file, name
            )
            raise ConfigException(msg)
        previous_task = task_parsing_context.previous_task
        previous_task_fields = previous_task.get_resulting_fields() if previous_task else None
        fields_ctxt = confighelper.get_literal_list(task_parsing_context, K_FIELDS, True)
        field_list = [ctxt.value for ctxt in fields_ctxt.value]
        task = DiscardFieldsTask(name, previous_task_fields, field_list)
        _validate_field_mapping(task, previous_task, task_parsing_context.current_file)
        return task

    @classmethod
    def get_task_type_string(cls):
        return K_DISCARD_FIELDS

    @classmethod
    def is_conditional(cls):
        return False

    def __init__(self, name, previous_task_fields, field_list):
        super(DiscardFieldsTask, self).__init__(name, None)
        self.field_list = field_list
        self.field_set = set(self.field_list)
        if previous_task_fields:
            self.resulting_fields = [field for field in previous_task_fields if field not in self.field_set]
        else:
            self.resulting_fields = None

    def __str__(self):
        return "DiscardFieldsTask(%s, %s, %s)" % (
            self.name, self.resulting_fields, self.field_list
        )

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.name == other.name,
            self.resulting_fields == other.resulting_fields,
            self.field_list == other.field_list
        ])

    def transform(self, row_ctxt):
        rowdict = row_ctxt.rowdict
        output = {k: v for k, v in rowdict.items() if k not in self.field_set}
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields
