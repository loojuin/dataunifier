"""
UppercaseTask module.
"""

from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper

K_UPPERCASE = "uppercase"
K_FIELDS = "fields"


def _validate_field_mapping(uppercase_task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_task_fields = set(previous_task.get_resulting_fields())
    for field in uppercase_task.fields:
        if field not in previous_task_fields:
            msg = 'Field "%s" is expected by %s task "%s", but was not found in resulting fields of ' \
                  '%s task "%s". (File "%s")' % (
                      field, K_UPPERCASE, uppercase_task.name, previous_task.get_task_type_string(), previous_task.name,
                      current_file
                  )
            raise ConfigException(msg)


class UppercaseTask(AbstractRegularTask):
    """
    Converts field values to uppercase.
    """

    @classmethod
    def create_from_config(cls, task_parsing_context):
        valid_keys = {K_FIELDS}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        name = task_parsing_context.task_name
        when = task_parsing_context.when
        previous_task = task_parsing_context.previous_task
        resulting_fields = previous_task.get_resulting_fields() if previous_task else None
        fields_ctxt = confighelper.get_literal_list(task_parsing_context, K_FIELDS, True)
        fields = [ctxt.value for ctxt in fields_ctxt.value]
        task = UppercaseTask(name, when, resulting_fields, fields)
        _validate_field_mapping(task, previous_task, task_parsing_context.current_file)
        return task

    @classmethod
    def get_task_type_string(cls):
        return K_UPPERCASE

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, resulting_fields, fields):
        self.resulting_fields = resulting_fields
        self.fields = fields
        super(UppercaseTask, self).__init__(name, when)

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return super(UppercaseTask, self).__eq__(other) and all([
            self.resulting_fields == other.resulting_fields,
            self.fields == other.fields
        ])

    def __str__(self):
        return "UppercaseTask(%s, %s, %s, %s)" % (
            self.name,
            self.when,
            self.resulting_fields,
            self.fields
        )

    def __repr__(self):
        return str(self)

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        output = rowdict.copy()
        for field in self.fields:
            if field not in rowdict:
                raise TransformationException('Could not find field "%s".' % field)
            output[field] = rowdict[field].upper()
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields
