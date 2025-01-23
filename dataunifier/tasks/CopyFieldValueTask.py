"""
CopyFieldValueTask module.
"""

from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper

K_COPY_FIELD_VALUE = "copy_field_value"
K_FROM_FIELD = "from_field"
K_TO_FIELDS = "to_fields"


def _validate_field_mapping(task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_fields = set(previous_task.get_resulting_fields())
    fields = [task.from_field]
    fields.extend(task.to_fields)
    for field in fields:
        if field not in previous_fields:
            msg = 'Field "%s" was expected by %s task "%s", but was not found in resulting fields of ' \
                  'preceding %s task "%s". (File "%s")' % (
                      field, K_COPY_FIELD_VALUE, task.name, previous_task.get_task_type_string(), previous_task.name,
                      current_file
                  )
            raise ConfigException(msg)


class CopyFieldValueTask(AbstractRegularTask):
    """
    Task that copies value of one field into another.
    """

    @classmethod
    def create_from_config(cls, task_parsing_context):
        valid_keys = {K_FROM_FIELD, K_TO_FIELDS}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        name = task_parsing_context.task_name
        when = task_parsing_context.when
        previous_task = task_parsing_context.previous_task
        resulting_fields = previous_task.get_resulting_fields() if previous_task else None
        from_field_ctxt = confighelper.get_literal(task_parsing_context, K_FROM_FIELD, True)
        from_field = from_field_ctxt.value
        to_fields_ctxt = confighelper.get_literal_list(task_parsing_context, K_TO_FIELDS, True)
        to_fields = [ctxt.value for ctxt in to_fields_ctxt.value]
        task = CopyFieldValueTask(name, when, resulting_fields, from_field, to_fields)
        _validate_field_mapping(task, previous_task, task_parsing_context.current_file)
        return task

    @classmethod
    def get_task_type_string(cls):
        return K_COPY_FIELD_VALUE

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, resulting_fields, from_field, to_fields):
        super(CopyFieldValueTask, self).__init__(name, when)
        self.resulting_fields = resulting_fields
        self.from_field = from_field
        self.to_fields = to_fields

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.name == other.name,
            self.when == other.when,
            self.resulting_fields == other.resulting_fields,
            self.from_field == other.from_field,
            self.to_fields == other.to_fields
        ])

    def __str__(self):
        return "CopyFieldValueTask(%s, %s, %s, %s, %s)" % (
            self.name, self.when, self.resulting_fields, self.from_field, self.to_fields
        )

    def __repr__(self):
        return str(self)

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        output = rowdict.copy()
        if self.from_field not in rowdict:
            raise TransformationException('Could not find field "%s".' % self.from_field)
        value = rowdict[self.from_field]
        for field in self.to_fields:
            if field not in output:
                raise TransformationException('Could not find field "%s".' % field)
            output[field] = value
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields
