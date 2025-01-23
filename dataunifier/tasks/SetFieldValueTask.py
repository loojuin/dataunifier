"""
SetFieldValueTask module.
"""

from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper

K_SET_FIELD_VALUE = "set_field_value"
K_FIELD = "field"
K_VALUE = "value"


def _validate_field_mapping(set_field_value_task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_task_fields = set(previous_task.get_resulting_fields())
    if set_field_value_task.field not in previous_task_fields:
        msg = 'Field "%s" is expected by %s task "%s" but was not found in resulting fields from ' \
              '%s task "%s". (File "%s")' % (
                  set_field_value_task.field, K_SET_FIELD_VALUE, set_field_value_task.name,
                  previous_task.get_task_type_string(), previous_task.name, current_file
              )
        raise ConfigException(msg)


class SetFieldValueTask(AbstractRegularTask):
    """
    Set the value of a field.
    """

    @classmethod
    def create_from_config(cls, task_parsing_context):
        valid_keys = {K_FIELD, K_VALUE}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        name = task_parsing_context.task_name
        when = task_parsing_context.when
        field_ctxt = confighelper.get_literal(task_parsing_context, K_FIELD, True)
        previous_task = task_parsing_context.previous_task
        resulting_fields = previous_task.get_resulting_fields() if previous_task else None
        field = field_ctxt.value
        value_ctxt = confighelper.get_literal(task_parsing_context, K_VALUE, True)
        value = value_ctxt.value
        task = SetFieldValueTask(name, when, resulting_fields, field, value)
        _validate_field_mapping(task, previous_task, task_parsing_context.current_file)
        return task

    @classmethod
    def get_task_type_string(cls):
        return K_SET_FIELD_VALUE

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, resulting_fields, field, value):
        self.resulting_fields = resulting_fields
        self.field = field
        self.value = value
        super(SetFieldValueTask, self).__init__(name, when)

    def __str__(self):
        return "SetFieldValueTask(%s, %s, %s, %s, %s)" % (
            self.name, self.when, self.resulting_fields, self.field, self.value
        )

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return super(SetFieldValueTask, self).__eq__(other) and all([
            self.resulting_fields == other.resulting_fields,
            self.field == other.field,
            self.value == other.value
        ])

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        output = rowdict.copy()
        if self.field not in rowdict:
            raise TransformationException('Could not find field "%s".' % self.field)
        output[self.field] = self.value
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields
