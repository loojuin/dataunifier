"""
ConcatenateFieldsTask module.
"""

from dataunifier.common.exceptions import ConfigException, TransformationException
from dataunifier.tasks.AbstractTask import AbstractRegularTask
from dataunifier.utils import confighelper

K_CONCATENATE_FIELDS = "concatenate_fields"
K_FIELDS = "fields"
K_TO_FIELD = "to_field"
K_WITH_STRING = "with_string"


def _validate_field_mapping(task, previous_task, current_file):
    if not (previous_task and previous_task.get_resulting_fields()):
        return
    previous_fields = set(previous_task.get_resulting_fields())
    fields = task.fields.copy()
    fields.append(task.to_field)
    for field in fields:
        if field not in previous_fields:
            msg = 'Field "%s" was expected by %s task "%s", but was not found in resulting fields ' \
                  'from preceding %s task "%s". (File "%s")' % (
                      field, K_CONCATENATE_FIELDS, task.name, previous_task.get_task_type_string(),
                      previous_task.name, current_file
                  )
            raise ConfigException(msg)


class ConcatenateFieldsTask(AbstractRegularTask):
    """
    A task that concatenates the value of two or more fields with a string, and writes the result to another field.
    """

    @classmethod
    def create_from_config(cls, task_parsing_context):
        valid_keys = {K_FIELDS, K_TO_FIELD, K_WITH_STRING}
        confighelper.check_invalid_keys(task_parsing_context, valid_keys)
        name = task_parsing_context.task_name
        when = task_parsing_context.when
        previous_task = task_parsing_context.previous_task
        resulting_fields = previous_task.get_resulting_fields() if previous_task else None
        fields_ctxt = confighelper.get_literal_list(task_parsing_context, K_FIELDS, True)
        fields = [ctxt.value for ctxt in fields_ctxt.value]
        to_field_ctxt = confighelper.get_literal(task_parsing_context, K_TO_FIELD, True)
        to_field = to_field_ctxt.value
        with_string_ctxt = confighelper.get_literal(task_parsing_context, K_WITH_STRING, True)
        with_string = with_string_ctxt.value
        task = ConcatenateFieldsTask(name, when, resulting_fields, fields, to_field, with_string)
        _validate_field_mapping(task, previous_task, task_parsing_context.current_file)
        return task

    @classmethod
    def get_task_type_string(cls):
        return K_CONCATENATE_FIELDS

    @classmethod
    def is_conditional(cls):
        return True

    def __init__(self, name, when, resulting_fields, fields, to_field, with_string):
        super(ConcatenateFieldsTask, self).__init__(name, when)
        self.resulting_fields = resulting_fields
        self.fields = fields
        self.to_field = to_field
        self.with_string = with_string

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, type(self)):
            return False
        return all([
            self.name == other.name,
            self.when == other.when,
            self.resulting_fields == other.resulting_fields,
            self.fields == other.fields,
            self.to_field == other.to_field,
            self.with_string == other.with_string
        ])

    def transform(self, row_ctxt):
        if self.when and not self.when.evaluate(row_ctxt):
            return row_ctxt
        rowdict = row_ctxt.rowdict
        output = rowdict.copy()
        for field in self.fields:
            if field not in rowdict:
                raise TransformationException('Could not find field "%s"' % field)
        values = [rowdict[field] for field in self.fields]
        concatenated_value = self.with_string.join(values)
        if self.to_field not in output:
            raise TransformationException('Could not find field "%s"' % self.to_field)
        output[self.to_field] = concatenated_value
        return row_ctxt.with_updated_rowdict(output)

    def get_resulting_fields(self):
        return self.resulting_fields
